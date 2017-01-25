from .. import CLIBaseTestCase


class DiscoverRunTestCase(CLIBaseTestCase):

    def test_discover_w_params(self):
        self.app.run([
            'discover-run', 'mycluster', 'openstack',
            '--parameters',
            'username=user',
            'password=qwerty',
            'tenant_name=admin',
            'auth_url=http://1.2.3.4'
        ])
        self.app.request.post.assert_called_once_with(
            'http://1.1.1.1:22/clusters/discover', json={
                'name': 'mycluster',
                'method': 'openstack',
                'parameters': {
                    'username': 'user',
                    'password': 'qwerty',
                    'tenant_name': 'admin',
                    'auth_url': 'http://1.2.3.4',
                }
            }
        )
        self.resp.raise_for_status.assert_called_once_with()

    def test_discover_wo_params(self):
        self.app.run(['discover-run', 'mycluster', 'openstack'])
        self.app.request.post.assert_called_once_with(
            'http://1.1.1.1:22/clusters/discover', json={
                'name': 'mycluster',
                'method': 'openstack',
                'parameters': {},
            }
        )
        self.resp.raise_for_status.assert_called_once_with()


class DiscoverListTestCase(CLIBaseTestCase):

    def test_discover_list(self):
        self.app.run(['discover-list'])

        self.app.request.get.assert_called_once_with(
            'http://1.1.1.1:22/clusters/discover'
        )
        self.resp.raise_for_status.assert_called_once_with()
