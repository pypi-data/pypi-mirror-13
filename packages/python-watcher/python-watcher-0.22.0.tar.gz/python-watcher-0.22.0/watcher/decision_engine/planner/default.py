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

from enum import Enum

from watcher._i18n import _LW
from watcher.common import exception
from watcher.common import utils
from watcher.decision_engine.actions import hypervisor_state
from watcher.decision_engine.actions import migration
from watcher.decision_engine.actions import nop
from watcher.decision_engine.actions import power_state
from watcher.decision_engine.planner import base
from watcher import objects

LOG = log.getLogger(__name__)


# TODO(jed) The default planner is a very simple planner
# https://wiki.openstack.org/wiki/NovaOrchestration/WorkflowEngines​


class Primitives(Enum):
    LIVE_MIGRATE = 'MIGRATE'
    COLD_MIGRATE = 'MIGRATE'
    POWER_STATE = 'POWERSTATE'
    HYPERVISOR_STATE = 'HYPERVISOR_STATE'
    NOP = 'NOP'


priority_primitives = {
    Primitives.NOP.value: 0,
    Primitives.HYPERVISOR_STATE.value: 1,
    Primitives.LIVE_MIGRATE.value: 2,
    Primitives.COLD_MIGRATE.value: 3,
    Primitives.POWER_STATE.value: 4,
}


class DefaultPlanner(base.BasePlanner):
    def create_action(self, action_plan_id, action_type, applies_to=None,
                      src=None,
                      dst=None,
                      parameter=None,
                      description=None):
        uuid = utils.generate_uuid()

        action = {
            'uuid': uuid,
            'action_plan_id': int(action_plan_id),
            'action_type': action_type,
            'applies_to': applies_to,
            'src': src,
            'dst': dst,
            'parameter': parameter,
            'description': description,
            'state': objects.action.Status.PENDING,
            'alarm': None,
            'next': None,
        }
        return action

    def schedule(self, context, audit_id, solution):
        LOG.debug('Create an action plan for the audit uuid')
        action_plan = self._create_action_plan(context, audit_id)

        actions = list(solution.actions)
        to_schedule = []

        for action in actions:
            if isinstance(action, migration.Migrate):
                # TODO(jed) type
                primitive = self.create_action(action_plan.id,
                                               Primitives.LIVE_MIGRATE.value,
                                               action.vm.uuid,
                                               action.src_hypervisor.
                                               uuid,
                                               action.dest_hypervisor.
                                               uuid,
                                               description="{0}".format(
                                                   action)
                                               )

            elif isinstance(action, power_state.ChangePowerState):
                primitive = self.create_action(action_plan_id=action_plan.id,
                                               action_type=Primitives.
                                               POWER_STATE.value,
                                               applies_to=action.target.uuid,
                                               parameter=action.
                                               powerstate.
                                               value,
                                               description="{0}".format(
                                                   action))
            elif isinstance(action, hypervisor_state.ChangeHypervisorState):
                primitive = self.create_action(action_plan_id=action_plan.id,
                                               action_type=Primitives.
                                               HYPERVISOR_STATE.value,
                                               applies_to=action.target.uuid,
                                               parameter=action.state.
                                               value,
                                               description="{0}".format(
                                                   action))
            elif isinstance(action, nop.Nop):
                primitive = self.create_action(action_plan_id=action_plan.id,
                                               action_type=Primitives.
                                               NOP.value,
                                               description="{0}".format(
                                                   action))
            else:
                raise exception.MetaActionNotFound()
            priority = priority_primitives[primitive['action_type']]
            to_schedule.append((priority, primitive))

        # scheduling
        scheduled = sorted(to_schedule, reverse=False, key=lambda x: (x[0]))
        if len(scheduled) == 0:
            LOG.warning(_LW("The action plan is empty"))
            action_plan.first_action_id = None
            action_plan.save()
        else:
            parent_action = self._create_action(context,
                                                scheduled[0][1],
                                                None)
            scheduled.pop(0)

            action_plan.first_action_id = parent_action.id
            action_plan.save()

            for s_action in scheduled:
                action = self._create_action(context, s_action[1],
                                             parent_action)
                parent_action = action
        return action_plan

    def _create_action_plan(self, context, audit_id):
        action_plan_dict = {
            'uuid': utils.generate_uuid(),
            'audit_id': audit_id,
            'first_action_id': None,
            'state': objects.action_plan.Status.RECOMMENDED
        }

        new_action_plan = objects.ActionPlan(context, **action_plan_dict)
        new_action_plan.create(context)
        new_action_plan.save()
        return new_action_plan

    def _create_action(self, context, _action, parent_action):
        action_description = str(_action)
        LOG.debug("Create a action for the following resquest : %s"
                  % action_description)

        new_action = objects.Action(context, **_action)
        new_action.create(context)
        new_action.save()

        if parent_action:
            parent_action.next = new_action.id
            parent_action.save()

        return new_action
