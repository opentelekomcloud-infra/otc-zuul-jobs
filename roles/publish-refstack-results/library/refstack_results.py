#!/usr/bin/python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

psycopg2 = None  # This line needs for unit tests
try:
    import psycopg2
    from psycopg2.extras import DictCursor, execute_values
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils.six import iteritems
from distutils.version import LooseVersion


DOCUMENTATION = r'''
---
module: refstack_results
short_description: Publish refstack results into PostgreSQL database
options:
  login_user:
    description:
      - The username used to authenticate with.
    type: str
    default: postgres
  login_password:
    description:
      - The password used to authenticate with.
    type: str
  login_host:
    description:
      - Host running the database.
    type: str
  port:
    description:
      - Database port to connect to.
    type: int
    default: 5432
    aliases: [ login_port ]
  db:
    description:
    - Name of database to connect to and run queries against.
    type: str
    aliases:
    - login_db
  results_file:
    description:
    - Path to a refstack results file (json)
    type: str
  run_id:
    description:
    - Run ID
    type: str
    required: true
  log_url:
    description:
    - Link to the logs location
    type: str
    required: true
author:
- Artem Goncharov (@gtema)
'''


def get_conn_params(module, params_dict, warn_db_default=True):
    """Get connection parameters from the passed dictionary.
    Return a dictionary with parameters to connect to PostgreSQL server.
    """
    # To use defaults values, keyword arguments must be absent, so
    # check which values are empty and don't include in the return dictionary
    params_map = {
        "login_host": "host",
        "login_user": "user",
        "login_password": "password",
        "port": "port",
    }

    # Might be different in the modules:
    if params_dict.get('db'):
        params_map['db'] = 'database'
    elif params_dict.get('database'):
        params_map['database'] = 'database'
    elif params_dict.get('login_db'):
        params_map['login_db'] = 'database'
    else:
        if warn_db_default:
            module.warn('Database name has not been passed, '
                        'used default database to connect to.')

    kw = dict((params_map[k], v) for (k, v) in iteritems(params_dict)
              if k in params_map and v != '' and v is not None)

    # If a login_unix_socket is specified, incorporate it here.
    is_localhost = False
    if "host" not in kw or kw["host"] is None or kw["host"] == "localhost":
        is_localhost = True
    if is_localhost and params_dict["login_unix_socket"] != "":
        kw["host"] = params_dict["login_unix_socket"]

    return kw


def ensure_required_libs(module):
    """Check required libraries."""
    if not HAS_PSYCOPG2:
        module.fail_json(msg=missing_required_lib('psycopg2'))

    if (
        module.params.get('ca_cert')
        and LooseVersion(psycopg2.__version__) < LooseVersion('2.4.3')
    ):
        module.fail_json(msg='psycopg2 must be at least 2.4.3 in '
                         'order to use the ca_cert parameter')


def connect_to_db(module, conn_params, autocommit=False, fail_on_conn=True):
    """Connect to a PostgreSQL database.
    Return psycopg2 connection object.
    """
    ensure_required_libs(module)

    db_connection = None
    try:
        db_connection = psycopg2.connect(**conn_params)
        if autocommit:
            if LooseVersion(psycopg2.__version__) >= LooseVersion('2.4.2'):
                db_connection.set_session(autocommit=True)
            else:
                db_connection.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        # Switch role, if specified:
        if module.params.get('session_role'):
            cursor = db_connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor)

            try:
                cursor.execute('SET ROLE "%s"' % module.params['session_role'])
            except Exception as e:
                module.fail_json(
                    msg="Could not switch role: %s" % to_native(e))
            finally:
                cursor.close()

    except TypeError as e:
        if 'sslrootcert' in e.args[0]:
            module.fail_json(msg='Postgresql server must be at least '
                                 'version 8.4 to support sslrootcert')

        if fail_on_conn:
            module.fail_json(
                msg="unable to connect to database: %s" % to_native(e))
        else:
            module.warn("PostgreSQL server is unavailable: %s" % to_native(e))
            db_connection = None

    except Exception as e:
        if fail_on_conn:
            module.fail_json(
                msg="unable to connect to database: %s" % to_native(e))
        else:
            module.warn("PostgreSQL server is unavailable: %s" % to_native(e))
            db_connection = None

    return db_connection


def execute_skip_error(cursor, query):
    try:
        cursor.execute(query)
    except Exception:
        pass


def main():
    argument_spec = dict(
        login_user=dict(default='postgres'),
        login_password=dict(default='', no_log=True),
        login_host=dict(default=''),
        login_unix_socket=dict(default=''),
        port=dict(type='int', default=5432, aliases=['login_port']),
        db=dict(type='str', aliases=['login_db']),
        results_file=dict(type='str', required=True),
        log_url=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    results_file = module.params['results_file']
    log_url = module.params['log_url']

    conn_params = get_conn_params(module, module.params)
    db_connection = connect_to_db(module, conn_params, autocommit=True)

    cursor = db_connection.cursor(cursor_factory=DictCursor)

    execute_skip_error(
        cursor,
        "CREATE TABLE refstack_run "
        "(id varchar(36), "
        "environment varchar(100), "
        "log_link text, "
        "run_time timestamp, "
        "PRIMARY KEY (id))"
    )

    execute_skip_error(
        cursor,
        "CREATE TABLE refstack_test_results "
        "(run_id varchar(36), "
        "test_uuid varchar(40), "
        "test_name text, "
        "status text, "
        "result text, "
        "CONSTRAINT run_fk FOREIGN KEY(run_id) "
        "REFERENCES refstack_run(id) "
        "ON DELETE cascade"
        ")"
    )

    execute_skip_error(
        cursor,
        "CREATE INDEX refstack_test_results_run_id_idx "
        "ON refstack_test_results (run_id)"
    )

    with open(results_file) as f:
        results = json.load(f)

    data = []
    run_id = results['run_id']
    changed = False
    for k, v in results['results'].items():
        data.append((
            run_id, k, v.get('name'), v.get('status'), v.get('result')))

    try:
        cursor.execute("INSERT INTO refstack_run "
                       "(id, environment, log_link, run_time) "
                       "VALUES (%s, %s, %s, now())",
                       (run_id, results['environment'],
                        log_url))

        query = (
            "INSERT INTO refstack_test_results "
            "(run_id, test_uuid, test_name, status, result) "
            " VALUES %s"
        )

        execute_values(cursor, query, data)
        changed = True
    except Exception as ex:
        changed = False
        module.fail_json(
            msg='Failed to insert data %s' % to_native(ex)
        )

    kw = dict(
        changed=changed,
    )

    cursor.close()
    db_connection.close()

    module.exit_json(**kw)


if __name__ == '__main__':
    main()
