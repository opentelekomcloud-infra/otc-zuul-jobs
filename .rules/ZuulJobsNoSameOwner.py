import re

from ansiblelint import AnsibleLintRule


class ZuulJobsNoSameOwner(AnsibleLintRule):

    id = 'ZUULJOBS0002'
    shortdesc = 'Owner should not be kept between executor and remote'
    description = """
Since there is no way to guarantee that the user and or group on the remote
node also exist on the executor and vice versa, owner and group should not
be preserved when transfering files between them.

See:
https://zuul-ci.org/docs/zuul-jobs/policy.html\
#preservation-of-owner-between-executor-and-remote
"""

    tags = {'zuul-jobs-no-same-owner'}

    def matchplay(self, file, play):
        results = []
        if file.get('type') not in ('tasks',
                                    'handlers',
                                    'playbooks'):
            return results

        results.extend(self.handle_play(play))
        return results

    def handle_play(self, task):
        results = []
        if 'block' in task:
            results.extend(self.handle_playlist(task['block']))
        else:
            results.extend(self.handle_task(task))
        return results

    def handle_playlist(self, playlist):
        results = []
        for play in playlist:
            results.extend(self.handle_play(play))
        return results

    def handle_task(self, task):
        results = []
        if 'synchronize' in task:
            if self.handle_synchronize(task):
                results.append(("", self.shortdesc))
        elif 'unarchive' in task:
            if self.handle_unarchive(task):
                results.append(("", self.shortdesc))

        return results

    def handle_synchronize(self, task):
        if task.get('delegate_to') is not None:
            return False

        synchronize = task['synchronize']
        archive = synchronize.get('archive', True)

        if synchronize.get('owner', archive) or\
           synchronize.get('group', archive):
            return True
        return False

    def handle_unarchive(self, task):
        unarchive = task['unarchive']
        delegate_to = task.get('delegate_to')

        if delegate_to == 'localhost' or\
           delegate_to != 'localhost' and 'remote_src' not in unarchive:
            if unarchive['src'].endswith('zip'):
                if '-X' in unarchive.get('extra_opts', []):
                    return True
            if re.search(r'.*\.tar(\.(gz|bz2|xz))?$', unarchive['src']):
                if '--no-same-owner' not in unarchive.get('extra_opts', []):
                    return True
        return False
