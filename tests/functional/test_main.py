from oslotest import base
from six.moves import configparser
from tempest.lib.cli import base as tempest_cli_base
from tempest.lib.cli import output_parser
import testtools


CONF = configparser.ConfigParser()
CONF.read("conf.ini")

skip_discovery_tests = False
try:
    auth_url = CONF.get('openstack', 'os_auth_url')
    user = CONF.get('openstack', 'os_username')
    tenant = CONF.get('openstack', 'os_tenant_name')
    password = CONF.get('openstack', 'os_password')
except configparser.NoOptionError:
    skip_discovery_tests = True


def cmd(action, flags='', params='', fail_ok=False,
        merge_stderr=False):
    return tempest_cli_base.execute('kostyor', action, flags, params,
                                    fail_ok, merge_stderr,
                                    '.tox/functional/bin')


def details_parser(output_lines):
    table = output_parser.table(output_lines)
    items = {}
    for value in table['values']:
        items[value[0]] = value[1]
    return items


class KostyorReadOnlyTestCase(base.BaseTestCase):
    def setUp(self):
        super(KostyorReadOnlyTestCase, self).setUp()
        self.cluster_list = output_parser.listing(cmd('cluster-list'))
        for cluster in self.cluster_list:
            if cluster['Cluster Name'] == 'test':
                self.cluster_id = self.cluster_list[0]['Cluster ID']

    def test_list_upgrade_versions__pre_created_server__list_not_empty(self):
        raw_versions = cmd('list-upgrade-versions')
        versions = output_parser.listing(raw_versions)
        self.assertNotEqual(0, len(versions))

    def test_cluster_list__pre_created_server__list_not_empty(self):
        self.assertTrue(len(self.cluster_list) > 0)

    def test_list_discovery_methods__check_output__list_not_empty(self):
        raw_methods = cmd('list-discovery-methods')
        methods = output_parser.listing(raw_methods)
        self.assertNotEqual(0, len(methods))

    def test_cluster_status__pre_created_server__check_attrs(self):
        raw_cluster = cmd('cluster-status {}'.format(self.cluster_id))
        cluster = details_parser(raw_cluster)
        self.assertEqual('test', cluster['Cluster Name'])
        self.assertEqual('mitaka', cluster['OpenStack Version'])
        self.assertEqual('READY FOR UPGRADE', cluster['Status'])

    def test_check_upgrade__pre_created_cluster__list_not_empty(self):
        raw_upgrade_versions = cmd('check-upgrade {}'.format(self.cluster_id))
        upgrade_versions = output_parser.listing(raw_upgrade_versions)[0]
        self.assertTrue("Available Upgrade Versions" in upgrade_versions)


class KostyorReadWriteTestCase(base.BaseTestCase):
    @testtools.skipIf(skip_discovery_tests,
                      'Need to set Keystone authentification parameters')
    def test_discover_cluster__openstack_method__success(self):
        command = ('discover-cluster openstack cluster-1'
                   ' --os-auth-url {auth_url}  --username {user}'
                   ' --tenant-name {tenant} --password {password}')
        raw_cluster = cmd(command.format(auth_url=auth_url,
                                         user=user,
                                         tenant=tenant,
                                         password=password))
        cluster = details_parser(raw_cluster)

        self.assertEqual('cluster-1', cluster['Name'])
        # TODO Fix when Kostyor will be able to determine cluster version
        self.assertEqual('NOT READY FOR UPGRADE', cluster['Status'])
        self.assertEqual('unknown', cluster['Version'])
