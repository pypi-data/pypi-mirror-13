# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
import os

from oslo_middleware._i18n import _LW
from oslo_middleware.healthcheck import pluginbase

LOG = logging.getLogger(__name__)


class DisableByFilesPortsHealthcheck(pluginbase.HealthcheckBaseExtension):
    """DisableByFilesPorts healthcheck middleware plugin

    This plugin checks presence of a file that is provided for a application
    running on a certain port to report if the service is unavailable
    or not.

    Example of middleware configuration:

    .. code-block:: ini

      [filter:healthcheck]
      paste.filter_factory = oslo_middleware:Healthcheck.factory
      path = /healthcheck
      backends = disable_by_files_ports
      disable_by_file_paths = 5000:/var/run/keystone/healthcheck_disable, \
            35357:/var/run/keystone/admin_healthcheck_disable
    """
    def __init__(self, conf):
        super(DisableByFilesPortsHealthcheck, self).__init__(conf)
        self.status_files = {}
        self.status_files.update(
            self._iter_paths_ports(self.conf.get('disable_by_file_paths')))

    @staticmethod
    def _iter_paths_ports(paths):
        if paths:
            for port_path in paths.split(","):
                port_path = port_path.strip()
                if port_path:
                    port, path = port_path.split(":")
                    port = int(port)
                    yield (port, path)

    def healthcheck(self, server_port):
        path = self.status_files.get(server_port)
        if not path:
            LOG.warning(_LW('DisableByFilesPorts healthcheck middleware'
                            ' enabled without disable_by_file_paths set'
                            ' for port %s') % server_port)
            return pluginbase.HealthcheckResult(available=True,
                                                reason="OK")
        else:
            if not os.path.exists(path):
                return pluginbase.HealthcheckResult(available=True,
                                                    reason="OK")
            else:
                return pluginbase.HealthcheckResult(available=False,
                                                    reason="DISABLED BY FILE")


class DisableByFileHealthcheck(pluginbase.HealthcheckBaseExtension):
    """DisableByFile healthcheck middleware plugin

    This plugin checks presence of a file to report if the service
    is unavailable or not.

    Example of middleware configuration:

    .. code-block:: ini

      [filter:healthcheck]
      paste.filter_factory = oslo_middleware:Healthcheck.factory
      path = /healthcheck
      backends = disable_by_file
      disable_by_file_path = /var/run/nova/healthcheck_disable
    """

    def healthcheck(self, server_port):
        path = self.conf.get('disable_by_file_path')
        if path is None:
            LOG.warning(_LW('DisableByFile healthcheck middleware enabled '
                            'without disable_by_file_path set'))
            return pluginbase.HealthcheckResult(
                available=True, reason="OK",
                details="No 'disable_by_file_path' configuration value"
                        " specified")
        elif not os.path.exists(path):
            return pluginbase.HealthcheckResult(
                available=True, reason="OK",
                details="Path '%s' was not found" % path)
        else:
            return pluginbase.HealthcheckResult(
                available=False, reason="DISABLED BY FILE",
                details="Path '%s' was found" % path)
