# -*- encoding: utf-8 -*-
# Copyright (c) 2015 b<>com
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

import mock
from mock import MagicMock

from watcher.common.exception import MetaActionNotFound
from watcher.common import utils

from watcher.db import api as db_api
from watcher.decision_engine.actions.base import BaseAction
from watcher.decision_engine.planner.default import DefaultPlanner
from watcher.decision_engine.solution.default import DefaultSolution
from watcher.decision_engine.strategy.strategies.basic_consolidation import \
    BasicConsolidation
from watcher.tests.db import base
from watcher.tests.db import utils as db_utils
from watcher.tests.decision_engine.strategy.strategies.faker_cluster_state\
    import FakerModelCollector
from watcher.tests.decision_engine.strategy.strategies.faker_metrics_collector\
    import FakerMetricsCollector
from watcher.tests.objects import utils as obj_utils


class SolutionFaker(object):
    @staticmethod
    def build():
        metrics = FakerMetricsCollector()
        current_state_cluster = FakerModelCollector()
        sercon = BasicConsolidation("basic", "Basic offline consolidation")
        sercon.ceilometer = MagicMock(
            get_statistics=metrics.mock_get_statistics)
        return sercon.execute(current_state_cluster.generate_scenario_1())


class SolutionFakerSingleHyp(object):
    @staticmethod
    def build():
        metrics = FakerMetricsCollector()
        current_state_cluster = FakerModelCollector()
        sercon = BasicConsolidation("basic", "Basic offline consolidation")
        sercon.ceilometer = MagicMock(
            get_statistics=metrics.mock_get_statistics)

        return sercon.execute(
            current_state_cluster.generate_scenario_3_with_2_hypervisors())


class TestActionScheduling(base.DbTestCase):
    scenarios = [
        (str(action_cls), {"fake_action": mock.Mock(spec=action_cls)})
        for action_cls in BaseAction.__subclasses__()]

    def test_schedule_actions(self):
        default_planner = DefaultPlanner()
        audit = db_utils.create_test_audit(uuid=utils.generate_uuid())
        dummy_solution = DefaultSolution()
        dummy_solution.add_change_request(self.fake_action)

        with mock.patch.object(
                DefaultPlanner, "create_action",
                wraps=default_planner.create_action) as m_create_action:
            action_plan = default_planner.schedule(
                self.context, audit.id, dummy_solution
            )

        self.assertIsNotNone(action_plan.uuid)
        self.assertEqual(m_create_action.call_count, 1)


class TestDefaultPlanner(base.DbTestCase):
    def setUp(self):
        super(TestDefaultPlanner, self).setUp()
        self.default_planner = DefaultPlanner()
        obj_utils.create_test_audit_template(self.context)

        p = mock.patch.object(db_api.BaseConnection, 'create_action_plan')
        self.mock_create_action_plan = p.start()
        self.mock_create_action_plan.side_effect = (
            self._simulate_action_plan_create)
        self.addCleanup(p.stop)

        q = mock.patch.object(db_api.BaseConnection, 'create_action')
        self.mock_create_action = q.start()
        self.mock_create_action.side_effect = (
            self._simulate_action_create)
        self.addCleanup(q.stop)

    def _simulate_action_plan_create(self, action_plan):
        action_plan.create()
        return action_plan

    def _simulate_action_create(self, action):
        action.create()
        return action

    def test_scheduler_w(self):
        audit = db_utils.create_test_audit(uuid=utils.generate_uuid())
        fake_solution = SolutionFaker.build()
        action_plan = self.default_planner.schedule(self.context,
                                                    audit.id, fake_solution)
        self.assertIsNotNone(action_plan.uuid)

    def test_schedule_raise(self):
        audit = db_utils.create_test_audit(uuid=utils.generate_uuid())
        fake_solution = SolutionFaker.build()
        fake_solution.actions[0] = "valeur_qcq"
        self.assertRaises(MetaActionNotFound, self.default_planner.schedule,
                          self.context, audit.id, fake_solution)

    def test_schedule_scheduled_empty(self):
        audit = db_utils.create_test_audit(uuid=utils.generate_uuid())
        fake_solution = SolutionFakerSingleHyp.build()
        action_plan = self.default_planner.schedule(self.context,
                                                    audit.id, fake_solution)
        self.assertIsNotNone(action_plan.uuid)

    def test_scheduler_warning_empty_action_plan(self):
        audit = db_utils.create_test_audit(uuid=utils.generate_uuid())
        fake_solution = SolutionFaker.build()
        action_plan = self.default_planner.schedule(self.context,
                                                    audit.id, fake_solution)
        self.assertIsNotNone(action_plan.uuid)
