#!/usr/bin/python
import os

import logging
import requests
import six
import sys

from cliff.lister import Lister
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.show import ShowOne


logging.getLogger("urllib3").setLevel(logging.WARNING)

host = os.environ.get('KOSTYOR_HOST', "localhost")
port = os.environ.get('KOSTYOR_PORT', 80)


def _make_request_with_cluster_id(http_method, endpoint, cluster_id):
    req_method = getattr(requests, http_method)
    return req_method('http://{}:{}/{}/{}'.format(host, port, endpoint,
                                                  cluster_id))


def _print_error_msg(resp):
    try:
        message = resp.json()['message']
    except (ValueError, KeyError):
        # if response doesn't contain valid error representation
        # just print its content
        message = resp.text
    print('HTTP {}: {}'.format(resp.status_code, message))


class KostyorApp(App):

    def __init__(self):
        super(KostyorApp, self).__init__(
            description='Kostyor cli app',
            version='0.1',
            command_manager=CommandManager('kostyor.cli'),
            deferred_help=True,
        )

        # There are two reasons why using session is a good idea here. The
        # first one is, session uses a pool with keep-alive connections so
        # any further requests to the same domain won't initiate a new
        # connection. The second reason is, it's configurable so we can
        # setup, for example, common headers here and do not pass them
        # across the code.
        self.request = requests.Session()
        self.baseurl = 'http://{0}:{1}'.format(host, port)

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)

        if err:
            self.LOG.debug('got an error: %s', err)

            if isinstance(err, requests.HTTPError):
                _print_error_msg(err.response)


class ClusterList(Lister):
    def take_action(self, parsed_args):
        columns = ('Cluster Name', 'Cluster ID', 'Status')
        data = self.app.request.get('{0}/clusters'.format(self.app.baseurl))
        clusters = data.json()
        if isinstance(clusters, dict):
            clusters = clusters['clusters']
        output = ((i['name'], i['id'], i['status']) for i in clusters)

        return (columns, output)


class ClusterStatus(ShowOne):
    description = ("Returns information about a cluster as a list of nodes "
                   "belonging to specified cluster and list of services "
                   "running on these nodes")
    action = "clusters"

    def get_parser(self, prog_name):
        parser = super(ClusterStatus, self).get_parser(prog_name)
        parser.add_argument('cluster_id')
        return parser

    def take_action(self, parsed_args):

        cluster_id = parsed_args.cluster_id
        columns = ('Cluster ID', 'Cluster Name', 'OpenStack Version',
                   'Status',)
        data = self.app.request.get(
            '{}/{}/{}'.format(self.app.baseurl, self.action, cluster_id))
        output = ()
        if data.status_code == 200:
            data = data.json()
            output = (data[i] for i in ['id', 'name', 'version',
                                        'status'])
        else:
            _print_error_msg(data)
        return (columns, output)

    @staticmethod
    def get_status(cluster_id):
        r = _make_request_with_cluster_id('get', ClusterStatus.action,
                                          cluster_id)
        if r.status_code != 200:
            message = r.json()['message']
            raise Exception('Failed to get cluster status: %s' % message)
        result = r.json()
        return result


class ClusterUpgrade(ShowOne):
    description = "Kicks off an upgrade of specified cluster"
    action = "upgrade-cluster"

    def get_parser(self, prog_name):
        parser = super(ClusterUpgrade, self).get_parser(prog_name)
        for arg_name in ['cluster_id', 'to_version']:
            parser.add_argument(arg_name)
        return parser

    def take_action(self, parsed_args):
        cluster_id = parsed_args.cluster_id
        to_version = parsed_args.to_version
        columns = ('Cluster ID', 'Upgrade Status',)
        request_str = '{}/upgrade-cluster/{}'.format(self.app.baseurl,
                                                     cluster_id)
        data = self.app.request.post(request_str,
                                     data={'version': to_version})
        output = ()
        if data.status_code == 201:
            data = data.json()
            output = (data['id'], data['status'],)
        else:
            _print_error_msg(data)

        return (columns, output)

    def upgrade(cluster_id, to_version):
        r = _make_request_with_cluster_id('post', 'upgrade-cluster',
                                          cluster_id)
        if r.status_code != 201:
            message = r.json()['message']
            raise Exception(message)
        ClusterStatus.get_status(cluster_id)


class ListUpgradeVersions(Lister):
    description = ("Show the supported versions that Kostyor is able to "
                   "upgrade")
    action = "list-upgrade-versions"

    def take_action(self, parsed_args):
        columns = ('From Version', 'To Version',)
        data = self.app.request.get(
            '{}/list-upgrade-versions'.format(self.app.baseurl)).json()
        data = [i.capitalize() for i in data]
        versions = ((data[i], data[i+1])
                    for i in six.moves.range(len(data) - 1))
        return (columns, versions)

    def list(cluster_id):
        r = _make_request_with_cluster_id('get', 'list-upgrade-versions')
        if r.status_code != 200:
            message = r.json()['message']
            raise Exception('Failed to get list of upgrade versions: %s'
                            % message)
        result = r.json()
        return result


class CheckUpgrade(Lister):
    description = ("Returns list of available versions cluster can be "
                   "upgraded to")
    action = "check-upgrade"

    def get_parser(self, prog_name):
        parser = super(CheckUpgrade, self).get_parser(prog_name)
        parser.add_argument('cluster_id')
        return parser

    def take_action(self, parsed_args):
        cluster_id = parsed_args.cluster_id
        columns = ('Available Upgrade Versions',)
        request_str = '{}/upgrade-versions/{}'.format(self.app.baseurl,
                                                      cluster_id)
        data = self.app.request.get(request_str)
        output = ()
        if data.status_code == 200:
            output = ((i.capitalize(),) for i in data.json())
        else:
            _print_error_msg(data)
        return (columns, output)


class HostList(Lister):
    description = ("Returns a list of hosts belonging to specified cluster")

    def get_parser(self, prog_name):
        parser = super(HostList, self).get_parser(prog_name)
        parser.add_argument('cluster_id')
        return parser

    def take_action(self, parsed_args):
        cluster_id = parsed_args.cluster_id
        columns = ('Host ID', 'Host Name')
        request_str = '{}/clusters/{}/hosts'.format(self.app.baseurl,
                                                    cluster_id)
        data = self.app.request.get(request_str)
        output = ()
        if data.status_code == 200:
            output = ((host['id'], host['hostname']) for host in data.json())
        else:
            _print_error_msg(data)
        return (columns, output)


class ServiceList(Lister):
    description = ("Returns a list of services belonging to specified cluster")

    def get_parser(self, prog_name):
        parser = super(ServiceList, self).get_parser(prog_name)
        parser.add_argument('cluster_id')
        return parser

    def take_action(self, parsed_args):
        cluster_id = parsed_args.cluster_id
        columns = ('Service ID', 'Service Name', 'Host ID', 'Version')
        request_str = '{}/clusters/{}/services'.format(self.app.baseurl,
                                                       cluster_id)
        data = self.app.request.get(request_str)
        output = ()
        if data.status_code == 200:
            def get_hosts(service):
                # TODO: backward compatibility, to be dropped
                if 'host_id' in data:
                    return service['host_id']
                return '\n'.join(service.get('hosts', []))

            output = ((service['id'],
                       service['name'],
                       get_hosts(service),
                       service['version']) for service in data.json())
        else:
            _print_error_msg(data)
        return (columns, output)


def main(argv=sys.argv[1:]):
    myapp = KostyorApp()
    return myapp.run(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
