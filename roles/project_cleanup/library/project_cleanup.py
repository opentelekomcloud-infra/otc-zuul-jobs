# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from datetime import datetime

import openstack

from ansible.module_utils.basic import AnsibleModule


def should_delete_resource(resource, filters):
    """Check if resource should be deleted based on filters."""
    if not filters:
        return True

    created_at_filter = filters.get('created_at')
    if not created_at_filter:
        return True

    created_at = getattr(resource, 'created_at', None)
    if not created_at:
        # No creation time available - delete to be safe (old resources)
        return True

    try:
        # Normalize both timestamps for comparison
        # OTC returns ISO 8601: "2026-04-28T17:00:00Z" or "2026-04-28T17:00:00"
        # Filter format: "2026-04-28 17:00:00"
        created_str = created_at.replace('T', ' ').replace('Z', '').split('.')[0]
        filter_str = created_at_filter.replace('T', ' ').replace('Z', '').split('.')[0]
        resource_time = datetime.strptime(created_str, '%Y-%m-%d %H:%M:%S')
        filter_time = datetime.strptime(filter_str, '%Y-%m-%d %H:%M:%S')
        return resource_time < filter_time
    except (ValueError, AttributeError, TypeError):
        # If we can't parse dates, delete to be safe
        return True


def cleanup_project_resources(conn, filters, dry_run):
    """Clean up project resources in dependency order."""
    resources = []
    errors = []

    def _try_cleanup(resource_type, list_fn, delete_fn, skip_fn=None):
        """Generic cleanup helper with error tracking."""
        try:
            for res in list_fn():
                if skip_fn and skip_fn(res):
                    continue
                if not should_delete_resource(res, filters):
                    continue
                name = getattr(res, 'name', None) or getattr(
                    res, 'floating_ip_address', None) or res.id
                resources.append(dict(
                    type=resource_type, name=name, id=res.id))
                if not dry_run:
                    try:
                        delete_fn(res)
                    except Exception as e:
                        errors.append(
                            "%s %s (%s): %s" % (resource_type, name,
                                                 res.id, str(e)))
        except Exception as e:
            errors.append("listing %s: %s" % (resource_type, str(e)))

    def _delete_router(router):
        """Delete router after removing all interfaces."""
        for port in conn.network.ports(device_id=router.id):
            if port.device_owner in ('network:router_interface',
                                     'network:router_interface_distributed'):
                for fixed_ip in port.fixed_ips:
                    try:
                        conn.network.remove_interface_from_router(
                            router.id, subnet_id=fixed_ip['subnet_id'])
                    except Exception:
                        # Try removing by port_id as fallback
                        try:
                            conn.network.remove_interface_from_router(
                                router.id, port_id=port.id)
                        except Exception:
                            pass
        # Clear gateway before deletion
        try:
            conn.network.update_router(
                router.id, external_gateway_info=None)
        except Exception:
            pass
        conn.network.delete_router(router.id)

    # 1. Servers
    _try_cleanup('Server', conn.compute.servers,
                 lambda s: conn.compute.delete_server(s.id))

    # 2. Floating IPs
    _try_cleanup('FloatingIP', conn.network.ips,
                 lambda f: conn.network.delete_ip(f.id))

    # 3. Routers (before ports/subnets - routers own ports)
    _try_cleanup('Router', conn.network.routers, _delete_router)

    # 4. Ports (skip router/DHCP/compute-owned ports)
    def _skip_port(port):
        if not port.device_owner:
            return False
        skip_owners = ('compute:', 'network:router', 'network:dhcp')
        return any(port.device_owner.startswith(o) for o in skip_owners)

    _try_cleanup('Port', conn.network.ports,
                 lambda p: conn.network.delete_port(p.id),
                 skip_fn=_skip_port)

    # 5. Subnets
    _try_cleanup('Subnet', conn.network.subnets,
                 lambda s: conn.network.delete_subnet(s.id))

    # 6. Networks (skip external/provider)
    def _skip_network(net):
        return (getattr(net, 'is_router_external', False)
                or getattr(net, 'provider_network_type', None))

    _try_cleanup('Network', conn.network.networks,
                 lambda n: conn.network.delete_network(n.id),
                 skip_fn=_skip_network)

    # 7. Volumes
    _try_cleanup('Volume', conn.block_storage.volumes,
                 lambda v: conn.block_storage.delete_volume(v.id))

    # 8. Volume snapshots
    _try_cleanup('Snapshot', conn.block_storage.snapshots,
                 lambda s: conn.block_storage.delete_snapshot(s.id))

    # 9. Security groups (skip default)
    _try_cleanup('SecurityGroup', conn.network.security_groups,
                 lambda sg: conn.network.delete_security_group(sg.id),
                 skip_fn=lambda sg: sg.name == 'default')

    return resources, errors


def run_module():
    module_args = dict(
        cloud=dict(type='raw', required=True),
        filters=dict(type='dict', required=False)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        conn = openstack.connect(module.params['cloud'])
        resources, errors = cleanup_project_resources(
            conn,
            module.params.get('filters'),
            module.check_mode
        )

        module.exit_json(
            changed=not module.check_mode and len(resources) > 0,
            resources=resources,
            errors=errors
        )
    except Exception as e:
        module.fail_json(msg=str(e))


def main():
    run_module()


if __name__ == '__main__':
    main()
