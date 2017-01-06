import six

from cliff.lister import Lister
from cliff.show import ShowOne

from kostyor_cli.commands.common import showarray, showone


class DiscoverList(Lister):
    """List available discovery methods."""

    columns = (
        (None, 'Method'),
    )

    @property
    def endpoint(self):
        return '{0}/clusters/discover'.format(self.app.baseurl)

    def take_action(self, parsed_args):
        resp = self.app.request.get(self.endpoint)
        resp.raise_for_status()
        return showarray(resp.json(), self.columns)


class DiscoverRun(ShowOne):

    columns = (
        ('id', 'ID'),
        ('name', 'Name'),
        ('version', 'OpenStack version'),
        ('status', 'Status'),
    )

    @property
    def endpoint(self):
        return '{0}/clusters/discover'.format(self.app.baseurl)

    def get_parser(self, prog_name):
        parser = super(DiscoverRun, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='Name of a cluster to be created.')
        parser.add_argument(
            'method',
            metavar='<method>',
            help='Discovery method to be used.')
        parser.add_argument(
            '-p', '--parameters',
            type=lambda x: x if six.PY3 else x.decode(),
            nargs='+',
            default=[],
            help='Key=Value pairs to be passed to discovering.')
        return parser

    def take_action(self, parsed_args):
        def to_kv(pair):
            if '=' not in pair:
                return (pair, None)
            return pair.split('=', 1)
        parameters = dict([to_kv(param) for param in parsed_args.parameters])

        resp = self.app.request.post(
            self.endpoint,
            json={
                'name': parsed_args.name,
                'method': parsed_args.method,
                'parameters': parameters,
            })
        resp.raise_for_status()
        return showone(resp.json(), self.columns)
