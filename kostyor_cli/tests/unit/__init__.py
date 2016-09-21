import mock
import oslotest.base

from kostyor_cli import main


class CLIBaseTestCase(oslotest.base.BaseTestCase):

    def setUp(self):
        super(CLIBaseTestCase, self).setUp()
        self.resp = mock.Mock()
        self.resp.status_code = 404
        self.resp.json = mock.MagicMock()

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

        self.app = main.KostyorApp()
        self.app.request = mock.Mock()
        self.app.request.post = mock.Mock(return_value=self.resp)
        self.app.request.put = mock.Mock(return_value=self.resp)
        self.app.request.get = mock.Mock(return_value=self.resp)
