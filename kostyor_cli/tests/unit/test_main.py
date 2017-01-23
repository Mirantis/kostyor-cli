import sys

import mock
from oslotest import base
import requests

from kostyor_cli.commands import common
from kostyor_cli import main

from . import CLIBaseTestCase


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


class MakeRequestTestCase(CLIBaseTestCase):
    def test__make_request_with_cluster_id__get_request__success(self):
        main._make_request_with_cluster_id('get', 'endpoint', 'cluster-id')
        requests.get.assert_called_once_with(
            'http://1.1.1.1:22/endpoint/cluster-id')

    def test__make_request_with_cluster_id__wrong_request_method__error(self):
        self.assertRaises(AttributeError, main._make_request_with_cluster_id,
                          'send', 'endpoint', 'cluster-id')


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

    @mock.patch.object(common, 'showarray')
    def test_host_list__existing_cluster__correct_request(self,
                                                          fake_showarray):
        fake_host = mock.Mock()
        self.resp.status_code = 200
        self.resp.json = mock.Mock()
        self.resp.json.return_value = fake_host
        self.app.run(self.command)
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        fake_showarray.assert_called_once_with(fake_host, mock.ANY)

    @mock.patch.object(common, 'showarray')
    def test_host_list__error_server_resp__print_error_msg(self,
                                                           fake_showarray):
        self.resp.raise_for_status = mock.Mock(side_effect=Exception())
        self.assertFalse(fake_showarray.called)
        self.assertRaises(Exception, self.app.run(self.command))
        self.app.request.get.assert_called_once_with(self.expected_request_str)
        self.assertFalse(fake_showarray.called)


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
