import abc

import six

from cliff.lister import Lister
from cliff.show import ShowOne

from kostyor_cli.commands.common import showarray, showone


class UpgradeList(Lister):
    """List upgrade tasks of OpenStack cluster."""

    columns = (
        ('id', 'UUID'),
        ('cluster_id', 'Cluster UUID'),
        ('status', 'Status'),
        ('from_version', 'From Version'),
        ('to_version', 'To Version'),
    )

    def _get_endpoint(self, cluster):
        resource = '{0}/upgrades'.format(self.app.baseurl)
        if cluster:
            resource = '{0}?cluster_id={1}'.format(resource, cluster)
        return resource

    def get_parser(self, prog_name):
        parser = super(UpgradeList, self).get_parser(prog_name)
        parser.add_argument(
            '--cluster', metavar='<cluster>', help='UUID of the cluster.')
        return parser

    def take_action(self, parsed_args):
        resp = self.app.request.get(self._get_endpoint(parsed_args.cluster))
        resp.raise_for_status()
        return showarray(resp.json(), self.columns)


class UpgradeShow(ShowOne):
    """Show upgrade status of OpenStack cluster."""

    columns = (
        ('id', 'UUID'),
        ('status', 'Status'),
        ('from_version', 'From Version'),
        ('to_version', 'To Version'),
        ('upgrade_start_time', 'Start Time'),
        ('upgrade_end_time', 'End Time'),
    )

    def _get_endpoint(self, upgrade):
        return '{0}/upgrades/{1}'.format(self.app.baseurl, upgrade)

    def get_parser(self, prog_name):
        parser = super(UpgradeShow, self).get_parser(prog_name)
        parser.add_argument(
            'upgrade', metavar='<upgrade>', help='UUID of the upgrade task.')
        return parser

    def take_action(self, parsed_args):
        resp = self.app.request.get(self._get_endpoint(parsed_args.upgrade))
        resp.raise_for_status()
        return showone(resp.json(), self.columns)


class UpgradeStart(ShowOne):
    """Start upgrade of OpenStack cluster."""

    columns = (
        ('id', 'UUID'),
        ('status', 'Status'),
        ('from_version', 'From Version'),
        ('to_version', 'To Version'),
        ('upgrade_start_time', 'Start Time'),
    )

    @property
    def endpoint(self):
        return '{0}/upgrades'.format(self.app.baseurl)

    def get_parser(self, prog_name):
        parser = super(UpgradeStart, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help='UUID of the cluster.')
        parser.add_argument(
            'to_version',
            metavar='<to-version>',
            help='OpenStack release upgrade to.')
        parser.add_argument(
            'driver',
            metavar='<driver>',
            nargs='?',
            help='Driver to be used.')
        return parser

    def take_action(self, parsed_args):
        payload = {
            'cluster_id': parsed_args.cluster,
            'to_version': parsed_args.to_version,
        }

        if parsed_args.driver is not None:
            payload['driver'] = parsed_args.driver

        resp = self.app.request.post(self.endpoint, json=payload)
        resp.raise_for_status()
        return showone(resp.json(), self.columns)


@six.add_metaclass(abc.ABCMeta)
class _UpgradeAction(ShowOne):

    columns = (
        ('id', 'UUID'),
        ('status', 'Status'),
        ('from_version', 'From Version'),
        ('to_version', 'To Version'),
        ('upgrade_start_time', 'Start Time'),
        ('upgrade_end_time', 'End Time'),
    )

    @property
    @abc.abstractmethod
    def action(self):
        """Action to trigger."""

    @property
    def endpoint(self):
        # FIXME: Unfortunately, the actions doesn't use <upgrade_id> parameter
        #        in endpoint uri. However, we've got to rethink API design
        #        so we can avoid such weird situations.
        return '{0}/upgrades/unused'.format(self.app.baseurl)

    def get_parser(self, prog_name):
        parser = super(_UpgradeAction, self).get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help='UUID of the cluster.')
        return parser

    def take_action(self, parsed_args):
        resp = self.app.request.put(
            self.endpoint,
            json={
                'cluster_id': parsed_args.cluster,
                'action': self.action,
            })
        resp.raise_for_status()
        return showone(resp.json(), self.columns)


class UpgradePause(_UpgradeAction):
    """Pause upgrade of OpenStack cluster."""

    action = 'pause'


class UpgradeContinue(_UpgradeAction):
    """Continue upgrade of OpenStack cluster."""

    action = 'continue'


class UpgradeRollback(_UpgradeAction):
    """Rollback upgrade of OpenStack cluster."""

    action = 'rollback'


class UpgradeCancel(_UpgradeAction):
    """Cancel upgrade of OpenStack cluster."""

    action = 'cancel'
