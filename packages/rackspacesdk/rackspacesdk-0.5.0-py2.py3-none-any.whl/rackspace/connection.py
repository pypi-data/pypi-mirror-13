# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack import connection
from openstack import profile as _profile
from rackspaceauth import v2


class Connection(connection.Connection):

    def __init__(self, region=None, profile=None, **kwargs):
        """Create a connection to the Rackspace Public Cloud

        This is a subclass of :class:`openstack.connection.Connection` that
        provides a specialization to enable the Rackspace authentication
        plugin as well as the Rackspace provider extension.

        :param str region: The region to interact with. Valid values include:
        IAD, ORD, DFW, SYD, HKG, and LON. **This parameter is
        required and will raise ValueError if it is omitted.**

        :raises: ValueError if no `region` is specified.
        """
        if profile is None:
            profile = _profile.Profile(plugins=["rackspace"])

        if region is None:
            raise ValueError("You must specify a region to work with.")

        profile.set_region(profile.ALL, region)

        global_services = ('cloudMetrics', 'cloudMetricsIngest',
                           'cloudMonitoring', 'rackCDN')

        for service in profile.get_services():
            if service.service_name in global_services:
                service.region = None

        username = kwargs.pop("username", None)
        tenant_id = kwargs.pop("tenant_id", None)

        if all([username, tenant_id]):
            raise ValueError("username and tenant_id cannot be used together")

        if username is None and tenant_id is None:
            raise ValueError("username or tenant_id must be specified")

        if username is not None:
            if "api_key" in kwargs:
                auth = v2.APIKey(username=username,
                                 api_key=kwargs.pop("api_key"))
            elif "password" in kwargs:
                auth = v2.Password(username=username,
                                   password=kwargs.pop("password"))
            else:
                raise ValueError(
                    "Either api_key or password must be passed with username")
        else:
            auth = v2.Token(tenant_id=tenant_id, token=kwargs.pop("token"))

        super(Connection, self).__init__(authenticator=auth,
                                         profile=profile,
                                         **kwargs)
