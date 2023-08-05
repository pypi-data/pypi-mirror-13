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

import logging
import decimal
import base64
import copy

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from cruddy.prototype import PrototypeHandler
from cruddy.response import CRUDResponse
from cruddy.exceptions import CruddyKeySchemaError, CruddyKeyNameError

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


class CRUD(object):

    SupportedOps = ["create", "update", "get", "delete",
                    "list", "search", "increment_counter"]

    def __init__(self, **kwargs):
        """
        Create a new CRUD handler.  The CRUD handler accepts the following
        parameters:

        * table_name - name of the backing DynamoDB table (required)
        * profile_name - name of the AWS credential profile to use when
          creating the boto3 Session
        * region_name - name of the AWS region to use when creating the
          boto3 Session
        * prototype - a dictionary of name/value pairs that will be used to
          initialize newly created items
        * supported_ops - a list of operations supported by the CRUD handler
          (choices are list, get, create, update, delete)
        * encrypted_attributes - a list of tuples where the first item in the
          tuple is the name of the attribute that should be encrypted and the
          second item in the tuple is the KMS master key ID to use for
          encrypting/decrypting the value
        * debug - if not False this will cause the raw_response to be left
          in the response dictionary
        """
        self.table_name = kwargs['table_name']
        profile_name = kwargs.get('profile_name')
        region_name = kwargs.get('region_name')
        placebo = kwargs.get('placebo')
        placebo_dir = kwargs.get('placebo_dir')
        placebo_mode = kwargs.get('placebo_mode', 'record')
        self.prototype = kwargs.get('prototype', dict())
        self._prototype_handler = PrototypeHandler(self.prototype)
        self.supported_ops = kwargs.get('supported_ops', self.SupportedOps)
        self.supported_ops.append('describe')
        self.encrypted_attributes = kwargs.get('encrypted_attributes', list())
        session = boto3.Session(profile_name=profile_name,
                                region_name=region_name)
        if placebo and placebo_dir:
            self.pill = placebo.attach(session, placebo_dir, debug=True)
            if placebo_mode == 'record':
                self.pill.record()
            else:
                self.pill.playback()
        else:
            self.pill = None
        ddb_resource = session.resource('dynamodb')
        self.table = ddb_resource.Table(self.table_name)
        self._indexes = {}
        self._analyze_table()
        self._debug = kwargs.get('debug', False)
        if self.encrypted_attributes:
            self._kms_client = session.client('kms')
        else:
            self._kms_client = None

    def _analyze_table(self):
        # First check the Key Schema
        if len(self.table.key_schema) != 1:
            msg = 'cruddy does not support RANGE keys'
            raise CruddyKeySchemaError(msg)
        if self.table.key_schema[0]['AttributeName'] != 'id':
            msg = 'cruddy expects the HASH to be id'
            raise CruddyKeyNameError(msg)
        # Now process any GSI's
        if self.table.global_secondary_indexes:
            for gsi in self.table.global_secondary_indexes:
                # find HASH of GSI, that's all we support for now
                # if the GSI has a RANGE, we ignore it for now
                if len(gsi['KeySchema']) == 1:
                    gsi_hash = gsi['KeySchema'][0]['AttributeName']
                    self._indexes[gsi_hash] = gsi['IndexName']

    # Because the Boto3 DynamoDB client turns all numeric types into Decimals
    # (which is actually the right thing to do) we need to convert those
    # Decimal values back into integers or floats before serializing to JSON.

    def _replace_decimals(self, obj):
        if isinstance(obj, list):
            for i in xrange(len(obj)):
                obj[i] = self._replace_decimals(obj[i])
            return obj
        elif isinstance(obj, dict):
            for k in obj.iterkeys():
                obj[k] = self._replace_decimals(obj[k])
            return obj
        elif isinstance(obj, decimal.Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        else:
            return obj

    def _encrypt(self, item):
        for encrypted_attr, master_key_id in self.encrypted_attributes:
            if encrypted_attr in item:
                response = self._kms_client.encrypt(
                    KeyId=master_key_id,
                    Plaintext=item[encrypted_attr])
                blob = response['CiphertextBlob']
                item[encrypted_attr] = base64.b64encode(blob)

    def _decrypt(self, item):
        for encrypted_attr, master_key_id in self.encrypted_attributes:
            if encrypted_attr in item:
                response = self._kms_client.decrypt(
                    CiphertextBlob=base64.b64decode(item[encrypted_attr]))
                item[encrypted_attr] = response['Plaintext']

    def _check_supported_op(self, op_name, response):
        if op_name not in self.supported_ops:
            response.status = 'error'
            response.error_type = 'UnsupportedOperation'
            response.error_message = 'Unsupported operation: {}'.format(
                op_name)
            return False
        return True

    def _call_ddb_method(self, method, kwargs, response):
        try:
            response.raw_response = method(**kwargs)
        except ClientError as e:
            LOG.debug(e)
            response.status = 'error'
            response.error_message = e.response['Error'].get('Message')
            response.error_code = e.response['Error'].get('Code')
            response.error_type = e.response['Error'].get('Type')
        except Exception as e:
            response.status = 'error'
            response.error_type = e.__class__.__name__
            response.error_code = None
            response.error_message = str(e)

    def _new_response(self):
        return CRUDResponse(self._debug)

    def describe(self, **kwargs):
        response = self._new_response()
        description = {
            'table_name': self.table_name,
            'supported_operations': copy.copy(self.supported_ops),
            'prototype': copy.deepcopy(self.prototype)
        }
        response.data = description
        return response

    def search(self, query, **kwargs):
        response = self._new_response()
        if self._check_supported_op('search', response):
            if '=' not in query:
                response.status = 'error'
                response.error_type = 'InvalidQuery'
                msg = 'Only the = operation is supported'
                response.error_message = msg
            else:
                key, value = query.split('=')
                if key not in self._indexes:
                    response.status = 'error'
                    response.error_type = 'InvalidQuery'
                    msg = 'Attribute {} is not indexed'.format(key)
                    response.error_message = msg
                else:
                    params = {'KeyConditionExpression': Key(key).eq(value),
                              'IndexName': self._indexes[key]}
                    self._call_ddb_method(self.table.query,
                                          params, response)
                    if response.status == 'success':
                        response.data = self._replace_decimals(
                            response.raw_response['Items'])
        response.prepare()
        return response

    def list(self, **kwargs):
        response = self._new_response()
        if self._check_supported_op('list', response):
            self._call_ddb_method(self.table.scan, {}, response)
            if response.status == 'success':
                response.data = self._replace_decimals(
                    response.raw_response['Items'])
        response.prepare()
        return response

    def get(self, id, **kwargs):
        decrypt = kwargs.get('decrypt', False)
        id_name = kwargs.get('id_name', 'id')
        response = self._new_response()
        if self._check_supported_op('get', response):
            if id is None:
                response.status = 'error'
                response.error_type = 'IDRequired'
                response.error_message = 'Get requires an id'
            else:
                params = {'Key': {id_name: id},
                          'ConsistentRead': True}
                self._call_ddb_method(self.table.get_item,
                                      params, response)
                if response.status == 'success':
                    if 'Item' in response.raw_response:
                        item = response.raw_response['Item']
                        if decrypt:
                            self._decrypt(item)
                        response.data = self._replace_decimals(item)
                    else:
                        response.status = 'error'
                        response.error_type = 'NotFound'
                        msg = 'item ({}) not found'.format(id)
                        response.error_message = msg
        response.prepare()
        return response

    def create(self, item, **kwargs):
        response = self._new_response()
        if self._prototype_handler.check(item, 'create', response):
            self._encrypt(item)
            params = {'Item': item}
            self._call_ddb_method(self.table.put_item,
                                  params, response)
            if response.status == 'success':
                response.data = item
        response.prepare()
        return response

    def update(self, item, **kwargs):
        response = self._new_response()
        if self._check_supported_op('update', response):
            if self._prototype_handler.check(item, 'update', response):
                self._encrypt(item)
                params = {'Item': item}
                self._call_ddb_method(self.table.put_item,
                                      params, response)
                if response.status == 'success':
                    response.data = item
        response.prepare()
        return response

    def increment_counter(self, id, counter_name, **kwargs):
        increment = kwargs.get('increment', 1)
        id_name = kwargs.get('id_name', 'id')
        response = self._new_response()
        if self._check_supported_op('increment_counter', response):
            params = {
                'Key': {id_name: id},
                'UpdateExpression': 'set #ctr = #ctr + :val',
                'ExpressionAttributeNames': {"#ctr": counter_name},
                'ExpressionAttributeValues': {
                    ':val': decimal.Decimal(increment)},
                'ReturnValues': 'UPDATED_NEW'
            }
            self._call_ddb_method(self.table.update_item, params, response)
            if response.status == 'success':
                if 'Attributes' in response.raw_response:
                    self._replace_decimals(response.raw_response)
                    attr = response.raw_response['Attributes'][counter_name]
                    response.data = attr
        response.prepare()
        return response

    def delete(self, id, **kwargs):
        id_name = kwargs.get('id_name', 'id')
        response = self._new_response()
        if self._check_supported_op('delete', response):
            params = {'Key': {id_name: id}}
            self._call_ddb_method(self.table.delete_item, params, response)
            response.data = 'true'
        response.prepare()
        return response

    def handler(self, operation=None, **kwargs):
        response = self._new_response()
        if operation is None:
            response.status = 'error'
            response.error_type = 'MissingOperation'
            response.error_message = 'You must pass an operation'
            return response
        operation = operation.lower()
        self._check_supported_op(operation, response)
        if response.status == 'success':
            method = getattr(self, operation, None)
            if callable(method):
                response = method(**kwargs)
            else:
                response.status == 'error'
                response.error_type = 'NotImplemented'
                msg = 'Operation: {} is not implemented'.format(operation)
                response.error_message = msg
        return response
