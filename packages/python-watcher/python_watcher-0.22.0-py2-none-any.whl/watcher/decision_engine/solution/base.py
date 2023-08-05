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


@six.add_metaclass(abc.ABCMeta)
class BaseSolution(object):
    def __init__(self):
        self._origin = None
        self._model = None
        self._efficacy = 0

    @property
    def efficacy(self):
        return self._efficacy

    @efficacy.setter
    def efficacy(self, e):
        self._efficacy = e

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, m):
        self._model = m

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, m):
        self._origin = m

    @abc.abstractmethod
    def add_change_request(self, r):
        raise NotImplementedError()

    @abc.abstractproperty
    def actions(self):
        raise NotImplementedError()
