from .. import CLIBaseTestCase


class UpgradeListTestCase(CLIBaseTestCase):

    def test_upgrade_list(self):
        self.app.run(['upgrade-list'])

        self.app.request.get.assert_called_once_with(
            'http://1.1.1.1:22/upgrades'
        )
        self.resp.raise_for_status.assert_called_once_with()

    def test_upgrade_list_w_cluster(self):
        self.app.run(['upgrade-list', '--cluster', '1234'])

        self.app.request.get.assert_called_once_with(
            'http://1.1.1.1:22/upgrades?cluster_id=1234'
        )
        self.resp.raise_for_status.assert_called_once_with()


class UpgradeShowTestCase(CLIBaseTestCase):

    def test_upgrade_show(self):
        self.app.run(['upgrade-show', '1234'])

        self.app.request.get.assert_called_once_with(
            'http://1.1.1.1:22/upgrades/1234'
        )
        self.resp.raise_for_status.assert_called_once_with()


class UpgradeStartTestCase(CLIBaseTestCase):

    def test_upgrade_start_correct_request(self):
        self.app.run(['upgrade-start', '1234', 'mitaka', 'openstack-ansible'])

        self.app.request.post.assert_called_once_with(
            'http://1.1.1.1:22/upgrades', json={
                'cluster_id': '1234',
                'to_version': 'mitaka',
                'driver': 'openstack-ansible',
            }
        )
        self.resp.raise_for_status.assert_called_once_with()

    def test_upgrade_start_correct_request_wo_driver(self):
        self.app.run(['upgrade-start', '1234', 'mitaka'])

        self.app.request.post.assert_called_once_with(
            'http://1.1.1.1:22/upgrades', json={
                'cluster_id': '1234',
                'to_version': 'mitaka',
            }
        )
        self.resp.raise_for_status.assert_called_once_with()


class UpgradeActionTestCase(CLIBaseTestCase):

    def _do_action(self, action):
        self.app.run(['upgrade-%s' % action, '1234'])
        self.app.request.put.assert_called_once_with(
            'http://1.1.1.1:22/upgrades/unused', json={
                'cluster_id': '1234',
                'action': action,
            }
        )
        self.resp.raise_for_status.assert_called_once_with()

    def test_upgrade_pause(self):
        self._do_action('pause')

    def test_upgrade_continue(self):
        self._do_action('continue')

    def test_upgrade_rollback(self):
        self._do_action('rollback')

    def test_upgrade_cancel(self):
        self._do_action('cancel')
