# Copyright (c) 2016 CloudNative, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import logging
import json

import boto3
import botocore.exceptions

LOG = logging.getLogger(__name__)


class LambdaClient(object):

    def __init__(self, func_name, profile_name=None,
                 region_name=None, debug=False):
        self.func_name = func_name
        self._lambda_client = None
        session = boto3.Session(
            profile_name=profile_name, region_name=region_name)
        self._lambda_client = session.client('lambda')
        self.debug = debug

    def invoke(self, payload):
        try:
            response = self._lambda_client.invoke(
                FunctionName=self.func_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            LOG.debug('response: %s', response)
            if response.get('StatusCode') == 200:
                payload = response['Payload'].read()
                LOG.debug('response.payload: %s', payload)
                try:
                    response = json.loads(payload)
                except ValueError:
                    # Probably a plain text response, or an error...
                    response = payload
                return response
            else:
                LOG.error('Call to lambda function %s failed', self.func_name)
                LOG.error(response.get('FunctionError'))
                LOG.error(response.get('ResponseMetadata'))
                return False
        except botocore.exceptions.ClientError:
            LOG.exception('Could not call Lambda function %s', self.func_name)
            raise

    def list(self):
        data = {'operation': 'list'}
        return self.invoke(data)

    def get(self, item_id, decrypt=False, id_name='id'):
        data = {'operation': 'get',
                id_name: item_id,
                'decrypt': decrypt}
        return self.invoke(data)

    def create(self, item):
        data = {'operation': 'create',
                'item': item}
        return self.invoke(data)

    def delete(self, item_id, id_name='id'):
        data = {'operation': 'get',
                id_name: item_id}
        return self.invoke(data)

    def search(self, query):
        data = {'operation': 'search',
                'query': query}
        return self.invoke(data)

    def increment(self, item_id, counter_name, increment=1, id_name='id'):
        data = {'operation': 'increment_counter',
                id_name: item_id,
                'counter_name': counter_name,
                'increment': increment}
        return self.invoke(data)
