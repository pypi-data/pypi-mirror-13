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

from watcher.decision_engine.actions.base import BaseAction
from watcher.decision_engine.model.hypervisor_state import HypervisorState


class ChangeHypervisorState(BaseAction):
    def __init__(self, target):
        '''The target host to change the state

        :param target: the target hypervisor uuid
        '''
        super(ChangeHypervisorState, self).__init__()
        self._target = target
        self._state = HypervisorState.ONLINE

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, p):
        self._target = p

    def __str__(self):
        return "{} ChangeHypervisorState => {}".format(self.target,
                                                       self.state)
