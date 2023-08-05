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
import abc
import six

""" Work in progress Helper to query metrics """


@six.add_metaclass(abc.ABCMeta)
class BaseClusterHistory(object):
    @abc.abstractmethod
    def statistic_aggregation(self, resource_id, meter_name, period,
                              aggregate='avg'):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_last_sample_values(self, resource_id, meter_name, limit=1):
        raise NotImplementedError()

    def query_sample(self, meter_name, query, limit=1):
        raise NotImplementedError()

    def statistic_list(self, meter_name, query=None, period=None):
        raise NotImplementedError()
