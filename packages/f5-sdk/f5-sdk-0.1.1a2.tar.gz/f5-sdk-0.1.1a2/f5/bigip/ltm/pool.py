# Copyright 2014-2016 F5 Networks Inc.
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

from f5.bigip.resource import Collection
from f5.bigip.resource import Resource


class MemberStateAlwaysRequiredOnUpdate(Exception):
    pass


class Pools(Collection):
    def __init__(self, ltm):
        super(Pools, self).__init__(ltm)
        self._meta_data['allowed_lazy_attributes'] = [Pool]
        self._meta_data['attribute_registry'] =\
            {'tm:ltm:pool:poolstate': Pool}


class Pool(Resource):
    def __init__(self, pool_s):
        super(Pool, self).__init__(pool_s)
        self._meta_data['required_json_kind'] = 'tm:ltm:pool:poolstate'
        self._meta_data['attribute_registry'] = {
            'tm:ltm:pool:memberscollectionstate': Members_s
        }


class Members_s(Collection):
    def __init__(self, pool):
        super(Members_s, self).__init__(pool)
        self._meta_data['allowed_lazy_attributes'] = [Member]
        self._meta_data['required_json_kind'] =\
            'tm:ltm:pool:members:memberscollectionstate'
        self._meta_data['attribute_registry'] =\
            {'tm:ltm:pool:members:membersstate': Member}


class Member(Resource):
    def __init__(self, member_s):
        super(Member, self).__init__(member_s)
        self._meta_data['required_json_kind'] =\
            'tm:ltm:pool:members:membersstate'
        self._meta_data['required_creation_parameters'].update(('partition',))

    def update(self, **kwargs):
        try:
            state = kwargs.pop('state')
        except KeyError:
            error_message = 'You must supply a value to the "state"' +\
                ' parameter if you do not wish to change the state then' +\
                ' pass "state=None".'
            raise MemberStateAlwaysRequiredOnUpdate(error_message)
        if state is None:
            self.__dict__.pop(u'state', '')
        else:
            self.state = state
        # This is an example implementation of read-only params
        self.__dict__.pop(u'ephemeral', '')
        self.__dict__.pop(u'address', '')
        self._update(**kwargs)
