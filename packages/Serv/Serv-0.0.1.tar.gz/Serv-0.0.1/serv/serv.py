import os
import re
import logging
import json

import sh
import ld
import click

from . import logger
from . import constants as const
from .init.base import Base


lgr = logger.init()


class Serv(object):
    def __init__(self, init_system=None, init_system_version=None,
                 verbose=False):
        if verbose:
            lgr.setLevel(logging.DEBUG)
        else:
            lgr.setLevel(logging.INFO)

        if not init_system or not init_system_version:
            result = self.lookup()
        self.init_sys = init_system or result[0][0]
        self.init_sys_ver = init_system_version or result[0][1]

        if not init_system:
            lgr.debug('Autodetected init system: {0}'.format(
                self.init_sys))
        if not init_system_version:
            lgr.debug('Autodetected init system version: {0}'.format(
                self.init_sys_ver))

    @staticmethod
    def _find_init_systems(init_system):
        init_systems = []

        def get_impl(impl):
            init_systems.append(impl)
            subclasses = impl.__subclasses__()
            if subclasses:
                for subclass in subclasses:
                    get_impl(subclass)

        lgr.debug('Finding init implementations...')
        get_impl(Base)
        for system in init_systems:
            if system.__name__.lower() == init_system:
                return system
        return None

    def create(self, cmd, name='', args='',
               description='no description given',
               user='root', group='root', env=None, overwrite=False,
               start=True):

        params = dict(
            init_sys=self.init_sys,
            init_sys_ver=self.init_sys_ver,
            cmd=cmd,
            name=name,
            args=args,
            description=description,
            user=user,
            group=group,
            env=json.loads(str(env)) or {}
        )

        lgr.info('Creating {0} Service: {1}...'.format(
            self.init_sys, name))
        init_system = self._find_init_systems(self.init_sys)
        s = init_system(lgr=lgr, **params)
        s.generate(overwrite=overwrite)
        s.install()
        if start:
            lgr.info('Starting Service: {0}'.format(name))
            s.start()
        lgr.info('Service created.')

    def remove(self, name):
        params = dict(
            init_sys=self.init_sys,
            init_sys_ver=self.init_sys_ver,
            name=name
        )

        lgr.info('Removing Service: {0}...'.format(name))
        init_system = self._find_init_systems(self.init_sys)
        s = init_system(lgr=lgr, **params)
        s.stop()
        s.uninstall()
        lgr.info('Service removed.')

    def status(self, name=''):
        params = dict(
            init_sys=self.init_sys,
            init_sys_ver=self.init_sys_ver,
            name=name
        )
        lgr.info('Retrieving Status...'.format(name))
        init_system = self._find_init_systems(self.init_sys)
        s = init_system(lgr=lgr, **params)
        return s.status(name)

    def lookup(self):
        lgr.debug('Looking up init method...')
        return self._lookup_by_mapping(ld.id().lower(), ld.major_version()) \
            or self._auto_lookup()

    @staticmethod
    def _get_upstart_version():
        try:
            output = sh.initctl.version()
        except:
            return
        version = re.search(r'(\d+((.\d+)+)+?)', str(output))
        if version:
            return str(version.group())
        return None

    @staticmethod
    def _get_systemctl_version():
        try:
            output = sh.systemctl('--version').split('\n')[0]
        except:
            return
        version = re.search(r'(\d+)', str(output))
        if version:
            return str(version.group())
        return None

    def _auto_lookup(self):
        init_systems = []
        if os.path.isdir('/usr/lib/systemd'):
            version = self._get_systemctl_version()
            if version:
                init_systems.append('systemd', version or 'default')
        if os.path.isdir('/usr/share/upstart'):
            version = self._get_upstart_version()
            if version:
                init_systems.append('upstart', version or 'default')
        if os.path.isdir('/etc/init.d'):
            init_systems.append('sysv', 'lsb-3.1')
        return init_systems

    @staticmethod
    def _lookup_by_mapping(distro, version):
        # init (upstart 1.12.1)
        if distro in ('arch'):
            version = 'any'
        return [const.DIST_TO_INITSYS.get(distro).get(version)] \
            or []


@click.group()
def main():
    pass


@click.command()
@click.option('-c', '--cmd', required=True,
              help='Absolute or in $PATH command to run.')
@click.option('--init-system', required=False,
              type=click.Choice(['upstart', 'systemd']),
              help='Init system to use.')
@click.option('--init-system-version', required=False, default='default',
              type=click.Choice(['lsb-3.1', '1.5', 'default']),
              help='Init system version to use.')
@click.option('-a', '--args', required=True,
              help='Arguments to pass to the command.')
@click.option('-e', '--env',
              help='Environment variables to load.')
@click.option('--overwrite', default=False, is_flag=True,
              help='Whether to overwrite the service if it already exists.')
@click.option('-s', '--start', default=False, is_flag=True,
              help='Start the service after creating it.')
@click.option('-v', '--verbose', default=False, is_flag=True)
def create(cmd, init_system, init_system_version, args, env, overwrite, start,
           verbose):
    """Creates (and maybe runs) service
    """
    logger.configure()
    Serv(init_system, init_system_version, verbose).create(
        cmd=cmd, args=args, env=env, overwrite=overwrite, start=start)


@click.command()
@click.option('-n', '--name',
              help='Name of service to remove.')
@click.option('--init-system', required=False,
              type=click.Choice(['upstart', 'systemd']),
              help='Init system to use.')
@click.option('-v', '--verbose', default=False, is_flag=True)
def remove(name, init_system, verbose):
    """Stops and Removes a service
    """
    logger.configure()
    Serv(init_system, verbose).remove(name)


@click.command()
@click.option('-n', '--name', required=False,
              help='Name of service to get status for. If omitted, will '
                   'returns the status for all services.')
@click.option('--init-system', required=False,
              type=click.Choice(['upstart', 'systemd']),
              help='Init system to use.')
@click.option('-v', '--verbose', default=False, is_flag=True)
def status(name, init_system, verbose):
    """Creates a service
    """
    logger.configure()
    status = Serv(init_system, verbose).status(name)
    print(json.dumps(status, indent=4, sort_keys=True))


main.add_command(create)
main.add_command(remove)
main.add_command(status)
