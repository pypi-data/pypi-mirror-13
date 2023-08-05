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
from oslo_log import log
from watcher.applier.execution.deploy_phase import DeployPhase
from watcher.applier.mapping.default import DefaultActionMapper
from watcher.applier.messaging.events import Events
from watcher.common.messaging.events.event import Event
from watcher.objects import Action
from watcher.objects.action_plan import Status

LOG = log.getLogger(__name__)


class ActionPlanExecutor(object):
    def __init__(self, manager_applier, context):
        self.manager_applier = manager_applier
        self.context = context
        self.deploy = DeployPhase(self)
        self.mapper = DefaultActionMapper()

    def get_primitive(self, action):
        return self.mapper.build_primitive_from_action(action)

    def notify(self, action, state):
        db_action = Action.get_by_uuid(self.context, action.uuid)
        db_action.state = state
        db_action.save()
        event = Event()
        event.type = Events.LAUNCH_ACTION
        event.data = {}
        payload = {'action_uuid': action.uuid,
                   'action_state': state}
        self.manager_applier.topic_status.publish_event(event.type.name,
                                                        payload)

    def execute(self, actions):
        for action in actions:
            try:
                self.notify(action, Status.ONGOING)
                primitive = self.get_primitive(action)
                result = self.deploy.execute_primitive(primitive)
                if result is False:
                    self.notify(action, Status.FAILED)
                    self.deploy.rollback()
                    return False
                else:
                    self.deploy.populate(primitive)
                    self.notify(action, Status.SUCCEEDED)
            except Exception as e:
                LOG.debug(
                    'The applier module failed to execute the action{0}  with '
                    'the exception {1} '.format(
                        action,
                        unicode(e)))

                LOG.error("Trigger a rollback")
                self.notify(action, Status.FAILED)
                self.deploy.rollback()
                return False
        return True
