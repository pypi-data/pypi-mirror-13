# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
topology garbage collection module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

import logging
from atexit import register
from traceback import format_exc
from collections import OrderedDict
from abc import ABCMeta, abstractmethod

from six import add_metaclass


log = logging.getLogger(__name__)


@addmetaclass()
class GarbageCollector(object):
    """
    """

    @abstractmethod
    def __init__(self):
        self.registry = []
        register(self.collect)

    def register(self, topology):
        self.registry.append(topology)

    @abstractmethod
    def check(self):
        pass

    def collect(self):
        # FIXME: Should we check that the reference counting
        #        is equal 1 using gc.get_referrers(obj)
        del self.registry[:]


__all__ = ['GarbageCollector']
