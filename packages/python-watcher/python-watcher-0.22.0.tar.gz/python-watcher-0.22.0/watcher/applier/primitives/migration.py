# -*- encoding: utf-8 -*-
# Copyright (c) 2015 b<>com
#
# Authors: Jean-Emile DARTOIS <jean-emile.dartois@b-com.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from keystoneclient.auth.identity import v3
from keystoneclient import session
from oslo_config import cfg

from watcher.applier.primitives.base import BasePrimitive
from watcher.applier.promise import Promise
from watcher.common.keystone import KeystoneClient
from watcher.common.nova import NovaClient
from watcher.decision_engine.planner.default import Primitives

CONF = cfg.CONF


class Migrate(BasePrimitive):
    def __init__(self, vm_uuid=None,
                 migration_type=None,
                 source_hypervisor=None,
                 destination_hypervisor=None):
        super(BasePrimitive, self).__init__()
        self.instance_uuid = vm_uuid
        self.migration_type = migration_type
        self.source_hypervisor = source_hypervisor
        self.destination_hypervisor = destination_hypervisor

    def migrate(self, destination):
        keystone = KeystoneClient()
        wrapper = NovaClient(keystone.get_credentials(),
                             session=keystone.get_session())
        instance = wrapper.find_instance(self.instance_uuid)
        if instance:
            project_id = getattr(instance, "tenant_id")

            creds2 = \
                {'auth_url': CONF.keystone_authtoken.auth_uri,
                 'username': CONF.keystone_authtoken.admin_user,
                 'password': CONF.keystone_authtoken.admin_password,
                 'project_id': project_id,
                 'user_domain_name': "default",
                 'project_domain_name': "default"}
            auth2 = v3.Password(auth_url=creds2['auth_url'],
                                username=creds2['username'],
                                password=creds2['password'],
                                project_id=creds2['project_id'],
                                user_domain_name=creds2[
                                    'user_domain_name'],
                                project_domain_name=creds2[
                                    'project_domain_name'])
            sess2 = session.Session(auth=auth2)
            wrapper2 = NovaClient(creds2, session=sess2)

            # todo(jed) remove Primitves
            if self.migration_type is Primitives.COLD_MIGRATE:
                return wrapper2.live_migrate_instance(
                    instance_id=self.instance_uuid,
                    dest_hostname=destination,
                    block_migration=True)
            elif self.migration_type is Primitives.LIVE_MIGRATE:
                return wrapper2.live_migrate_instance(
                    instance_id=self.instance_uuid,
                    dest_hostname=destination,
                    block_migration=False)

    @Promise
    def execute(self):
        return self.migrate(self.destination_hypervisor)

    @Promise
    def undo(self):
        return self.migrate(self.source_hypervisor)
