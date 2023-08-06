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

from f5.bigip.net.arp import ARP
from f5.bigip.net.interface import Interface
from f5.bigip.net.l2gre import L2GRE
from f5.bigip.net.route import Route
from f5.bigip.net.selfip import SelfIPCollection
from f5.bigip.net.vlan import VLANCollection
from f5.bigip.net.vxlan import VXLAN
from f5.bigip.resource import OrganizingCollection

base_uri = 'net/'


class Net(OrganizingCollection):
    def __init__(self, bigip):
        super(Net, self).__init__(bigip)
        self._meta_data['allowed_lazy_attributes'] = [
            ARP, Interface, L2GRE,
            Route, SelfIPCollection, VLANCollection, VXLAN
        ]
