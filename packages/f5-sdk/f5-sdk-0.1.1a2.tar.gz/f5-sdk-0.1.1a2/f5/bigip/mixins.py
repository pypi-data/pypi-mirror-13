# Copyright 2015-2016 F5 Networks Inc.
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
# NOTE:  Code taken from Effective Python Item 26


class ToDictMixin(object):
    traversed = {}
    Containers = tuple, list, set, frozenset, dict

    def to_dict(self):
        ToDictMixin.traversed = {}
        return self._to_dict()

    def _to_dict(self):
        result = self._traverse_dict(self.__dict__)
        return result

    def _traverse_dict(self, instance_dict):
        output = {}
        for key, value in instance_dict.items():
            output[key] = self._traverse(key, value)
        return output

    def _traverse(self, key, value):
        if isinstance(value, ToDictMixin.Containers) or\
           hasattr(value, '__dict__'):
            if id(value) in ToDictMixin.traversed:
                return ToDictMixin.traversed[id(value)]
            else:
                ToDictMixin.traversed[id(value)] = ['TraversalRecord', key]
        if isinstance(value, ToDictMixin):
            return value._to_dict()
        elif isinstance(value, dict):
            return self._traverse_dict(value)
        elif isinstance(value, list):
            return [self._traverse(key, item) for item in value]
        elif hasattr(value, '__dict__'):
            return self._traverse_dict(value.__dict__)
        else:
            return value


class LazyAttributesRequired(Exception):
    pass


class LazyAttributeMixin(object):
    def __getattr__(self, name):
        # ensure this object supports lazy attrs.
        cls_name = self.__class__.__name__
        if '_meta_data' not in self.__dict__:
            error_message = '%r does not have self._meta_data' % cls_name
            raise LazyAttributesRequired(error_message)
        elif 'allowed_lazy_attributes' not in self._meta_data:
            error_message = ('"allowed_lazy_attributes" not in',
                             'self._meta_data for class %s' % cls_name)
            raise LazyAttributesRequired(error_message)

        # ensure the requested attr is present
        lower_attr_names =\
            [la.__name__.lower() for la in
                self._meta_data['allowed_lazy_attributes']]
        if name not in lower_attr_names:
            error_message = "'%s' object has no attribute '%s'"\
                % (self.__class__, name)
            raise AttributeError(error_message)

        # Instantiate and potentially set the attr on the object
        # Issue #112 -- Only call setattr here if the lazy attribute
        # is NOT a `Resource`.  This should allow for only 1 ltm attribute
        # but many nat attributes just like the BIGIP device.
        for lazy_attribute in self._meta_data['allowed_lazy_attributes']:
            if name == lazy_attribute.__name__.lower():
                attribute = lazy_attribute(self)
                # Use the name of ResourceResource because importing causes
                # a circular reference
                bases = [base.__name__ for base in lazy_attribute.__bases__]
                if 'Resource' not in bases:
                    setattr(self, name, attribute)
                return attribute


class ExclusiveAttributesMixin(object):
    def __setattr__(self, key, value):
        '''Remove any of the existing exclusive attrs from the object

        Objects attributes can be exclusive for example disable/enable.  So
        we need to make sure objects only have one of these attributes at
        at time so that the updates won't fail.
        '''
        if '_meta_data' in self.__dict__:
            # Sometimes this is called prior to full object construction
            for attr_set in self._meta_data['exclusive_attributes']:
                if key in attr_set:
                    new_set = set(attr_set) - set([key])
                    [self.__dict__.pop(n, '') for n in new_set]
        # Now set the attribute
        super(ExclusiveAttributesMixin, self).__setattr__(key, value)
