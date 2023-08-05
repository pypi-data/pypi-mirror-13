# Copyright (c) 2016 CloudNative, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cruddy.calculatedvalue import CalculatedValue


class PrototypeHandler(object):

    def __init__(self, prototype):
        self.prototype = prototype

    def check(self, item, operation, response):
        for key in self.prototype:
            value = self.prototype[key]
            cv = CalculatedValue.check(value)
            if cv:
                if cv.operation == operation:
                    item[key] = cv.value
                elif cv.operation == 'update' and operation == 'create':
                    item[key] = cv.value
            else:
                if isinstance(value, type):
                    # a Python type was provided as the prototype value
                    # if no value is provided, create a default from the type
                    if key not in item:
                        item[key] = value()
                    else:
                        # check to see if current value in item is of that type
                        if not isinstance(item[key], value):
                            response.status = 'error'
                            response.error_type = 'InvalidType'
                            msg = 'Attribute {} must be of type {}'.format(
                                key, value)
                            response.error_message = msg
                            return False
                else:
                    # a Python object was provided as the prototype value
                    # so if the item has a value for that attribute name
                    # check to see if it is the right type
                    if key in item:
                        if type(item[key]) != type(value):
                            response.status = 'error'
                            response.error_type = 'InvalidType'
                            msg = 'Attribute {} must be of type {}'.format(
                                key, type(value))
                            response.error_message = msg
                            return False
                    else:
                        item[key] = value
        return True
