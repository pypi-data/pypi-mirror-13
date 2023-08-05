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

from watcher.applier.mapping.base import BaseActionMapper
from watcher.applier.primitives.change_nova_service_state import \
    ChangeNovaServiceState
from watcher.applier.primitives.migration import Migrate
from watcher.applier.primitives.nop import Nop
from watcher.applier.primitives.power_state import ChangePowerState
from watcher.common.exception import ActionNotFound
from watcher.decision_engine.planner.default import Primitives


class DefaultActionMapper(BaseActionMapper):
    def build_primitive_from_action(self, action):
        if action.action_type == Primitives.COLD_MIGRATE.value:
            return Migrate(action.applies_to, Primitives.COLD_MIGRATE,
                           action.src,
                           action.dst)
        elif action.action_type == Primitives.LIVE_MIGRATE.value:
            return Migrate(action.applies_to, Primitives.COLD_MIGRATE,
                           action.src,
                           action.dst)
        elif action.action_type == Primitives.HYPERVISOR_STATE.value:
            return ChangeNovaServiceState(action.applies_to, action.parameter)
        elif action.action_type == Primitives.POWER_STATE.value:
            return ChangePowerState()
        elif action.action_type == Primitives.NOP.value:
            return Nop()
        else:
            raise ActionNotFound()
