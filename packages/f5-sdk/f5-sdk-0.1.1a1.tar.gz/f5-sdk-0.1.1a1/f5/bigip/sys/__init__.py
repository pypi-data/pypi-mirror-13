# Copyright 2015 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from f5.bigip.resource import OrganizingCollection
from f5.bigip.sys.application import ApplicationCollection
from f5.bigip.sys.folder import FolderCollection
from f5.bigip.sys.stat import Stat
from f5.bigip.sys.system import System


base_uri = 'sys/'


class Sys(OrganizingCollection):
    def __init__(self, bigip):
        super(Sys, self).__init__(bigip)
        self._meta_data['allowed_lazy_attributes'] = [
            FolderCollection,
            ApplicationCollection, Stat, System
        ]
