import sys

import mock
from oslotest import base
import requests

from kostyor_cli import main


class PrintErrorMsgTestCase(base.BaseTestCase):

    @mock.patch('sys.stdout.write', mock.Mock())
    def test__print_error_msg__http_error_handling__success_json(self):
        resp = mock.Mock()
        resp.status_code = 400
        resp.json = mock.Mock(return_value={'message': 'Bad request'})
        main._print_error_msg(resp)
        sys.stdout.write.assert_any_call('HTTP 400: Bad request')

    @mock.patch('sys.stdout.write', mock.Mock())
    def test__print_error_msg__http_error_handling__success_plain(self):
        resp = mock.Mock()
        resp.status_code = 400
        resp.json = mock.Mock(side_effect=ValueError('invalid json'))
        resp.text = 'Bad request'
        main._print_error_msg(resp)
        sys.stdout.write.assert_any_call('HTTP 400: Bad request')


class CLIBaseTestCase(base.BaseTestCase):
    def setUp(self):
        super(CLIBaseTestCase, self).setUp()
        self.resp = mock.Mock()
        self.resp.status_code = 404
        self.resp.json = mock.MagicMock()
        self.app = main.KostyorApp()

        host_patcher = mock.patch('kostyor_cli.main.host', '1.1.1.1')
        port_patcher = mock.patch('kostyor_cli.main.port', '22')
        stdout_patcher = mock.patch('sys.stdout.write')
        print_msg_patcher = mock.patch('kostyor_cli.main._print_error_msg')
        post_patcher = mock.patch('requests.post',
                                  mock.Mock(return_value=self.resp))
        get_patcher = mock.patch('requests.get',
                                 mock.Mock(return_value=self.resp))
        for patcher in [host_patcher, port_patcher, stdout_patcher,
                        print_msg_patcher, post_patcher, get_patcher]:
            patcher.start()
            self.addCleanup(patcher.stop)

        self.app.request = mock.Mock()
        self.app.request.post = mock.Mock(return_value=self.resp)
        self.app.request.put = mock.Mock(return_value=self.resp)
        self.app.request.get = mock.Mock(return_value=self.resp)


class MakeRequestTestCase(CLIBaseTestCase):
    def test__make_request_with_cluster_id__get_request__success(self):
        main._make_request_with_cluster_id('get', 'endpoint', 'cluster-id')
        requests.get.assert_called_once_with(
            'http://1.1.1.1:22/endpoint/cluster-id')

    def test__make_request_with_cluster_id__wrong_request_method__error(self):
        self.assertRaises(AttributeError, main._make_request_with_cluster_id,
                          'send', 'endpoint', 'cluster-id')


class ClusterDiscoveryTestCase(CLIBaseTestCase):
    def setUp(self):
        super(ClusterDiscoveryTestCase, self).setUp()
        self.expected_request_params = {
            'method': 'openstack',
            'cluster_name': 'new-cluster',
            'auth_url': 'http://1.2.3.4',
            'username': 'admin',
            'tenant_name': 'admin',
            'password': 'qwerty',
        }
        self.expected_request_str = 'http://1.1.1.1:22/discover-cluster'
        self.command = ['discover-cluster',
                        'openstack',
                        'new-cluster',
                        '--os-auth-url=http://1.2.3.4',
                        '--username=admin',
                        '--tenant-name=admin',
                        '--password=qwerty']

    def test_discover_cluster__expected_args__correct_request(self):
        self.resp.status_code = 201
        self.app.run(self.command)
        self.app.request.post.assert_called_once_with(
            self.expected_request_str,
            data=self.expected_request_params)
        self.assertFalse(main._print_error_msg.called)

    def test_discover_cluster__error_server_resp__print_error_msg(self):
        self.expected_request_params['method'] = 'fake-method'
        self.command[1] = 'fake-method'
        self.app.run(self.command)
        self.app.request.post.assert_called_once_with(
            self.expected_request_str,
            data=self.expected_request_params)
        main._print_error_msg.assert_called_once_with(self.resp)


class ClusterListTestCase(CLIBaseTestCase):
    @mock.patch('requests.get', mock.MagicMock())
    def test_cluster_list__run_without_args__correct_request(self):
        expected_request_str = 'http://1.1.1.1:22/clusters'
        command = ['cluster-list', ]
        self.app.run(command)
        self.app.request.get.assert_called_once_with(expected_request_str)


class ClusterStatusTestCase(CLIBaseTestCase):
    def setUp(self):
        super(ClusterStatusTestCase, self).setUp()
        self.expected_request_str = 'http://1.1.1.1:22/clusters/1234'
        self.command = ['cluster-status', '1234']

    def test_cluster_status__expected_args__correct_request(self):
        self.resp.status_code = 200
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(
            self.expected_request_str
        )
        self.assertFalse(main._print_error_msg.called)

    def test_cluster_status__error_resp__print_error_msg(self):
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(
            self.expected_request_str
        )
        main._print_error_msg.assert_called_once_with(self.resp)


class ClusterUpgradeTestCase(CLIBaseTestCase):
    def setUp(self):
        super(ClusterUpgradeTestCase, self).setUp()
        self.expected_params = {'version': 'mitaka'}
        self.expected_request_str = 'http://1.1.1.1:22/upgrade-cluster/1234'
        self.command = ['upgrade-cluster',
                        '1234',
                        'mitaka']

    def test_upgrade_cluster__expected_args__correct_request(self):
        self.resp.status_code = 201
        self.app.run(self.command)
        self.app.request.post.assert_called_once_with(
            self.expected_request_str,
            data=self.expected_params
        )
        self.assertFalse(main._print_error_msg.called)

    def test_upgrade_cluster__error_server_resp__print_error_msg(self):
        self.app.run(self.command)
        self.app.request.post.assert_called_once_with(
            self.expected_request_str,
            data=self.expected_params
        )
        main._print_error_msg.assert_called_once_with(self.resp)


class CheckUpgradeTestCase(CLIBaseTestCase):
    def setUp(self):
        super(CheckUpgradeTestCase, self).setUp()
        self.expected_request_str = 'http://1.1.1.1:22/upgrade-versions/1234'
        self.command = ['check-upgrade',
                        '1234']

    def test_check_upgrade__expected_args__correct_request(self):
        self.resp.status_code = 200
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        self.assertFalse(main._print_error_msg.called)

    def test_check_upgrade__error_server_resp__print_error_msg(self):
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        main._print_error_msg.assert_called_once_with(self.resp)


class ListUpgradeVersionsTestCase(CLIBaseTestCase):
    def setUp(self):
        super(ListUpgradeVersionsTestCase, self).setUp()
        self.expected_request_str = 'http://1.1.1.1:22/list-upgrade-versions'
        self.command = ['list-upgrade-versions']

    def test_list_upgrade__run_without_args__correct_request(self):
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        self.assertFalse(main._print_error_msg.called)


class HostListTestCase(CLIBaseTestCase):
    def setUp(self):
        super(HostListTestCase, self).setUp()
        self.command = ['host-list', '1234']
        self.expected_request_str = 'http://1.1.1.1:22/clusters/1234/hosts'

    def test_host_list__existing_cluster__correct_request(self):
        self.resp.status_code = 200
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        self.assertFalse(main._print_error_msg.called)

    def test_host_list__error_server_resp__print_error_msg(self):
        requests.get.return_value = self.resp
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        main._print_error_msg.assert_called_once_with(self.resp)


class ServiceListTestCase(CLIBaseTestCase):
    def setUp(self):
        super(ServiceListTestCase, self).setUp()
        self.command = ['service-list', '1234']
        self.expected_request_str = 'http://1.1.1.1:22/clusters/1234/services'

    def test_service_list__existing_cluster__correct_request(self):
        self.resp.status_code = 200
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        self.assertFalse(main._print_error_msg.called)

    def test_service_list__error_server_resp__print_error_msg(self):
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        main._print_error_msg.assert_called_once_with(self.resp)
