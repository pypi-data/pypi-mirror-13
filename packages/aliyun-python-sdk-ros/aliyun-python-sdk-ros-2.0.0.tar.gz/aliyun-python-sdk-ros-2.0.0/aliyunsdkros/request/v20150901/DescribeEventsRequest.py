# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from aliyunsdkcore.request import RoaRequest
class DescribeEventsRequest(RoaRequest):

	def __init__(self):
		RoaRequest.__init__(self, 'ROS', '2015-09-01', 'DescribeEvents')
		self.set_uri_pattern('/stacks/[StackName]/[StackId]/events')
		self.set_method('GET')

	def get_StackName(self):
		return self.get_path_params().get('StackName')

	def set_StackName(self,StackName):
		self.add_path_param('StackName',StackName)

	def get_StackId(self):
		return self.get_path_params().get('StackId')

	def set_StackId(self,StackId):
		self.add_path_param('StackId',StackId)

	def get_ResourceStatus(self):
		return self.get_query_params().get('ResourceStatus')

	def set_ResourceStatus(self,ResourceStatus):
		self.add_query_param('ResourceStatus',ResourceStatus)

	def get_ResourceName(self):
		return self.get_query_params().get('ResourceName')

	def set_ResourceName(self,ResourceName):
		self.add_query_param('ResourceName',ResourceName)

	def get_ResourceType(self):
		return self.get_query_params().get('ResourceType')

	def set_ResourceType(self,ResourceType):
		self.add_query_param('ResourceType',ResourceType)

	def get_PageSize(self):
		return self.get_query_params().get('PageSize')

	def set_PageSize(self,PageSize):
		self.add_query_param('PageSize',PageSize)

	def get_PageNumber(self):
		return self.get_query_params().get('PageNumber')

	def set_PageNumber(self,PageNumber):
		self.add_query_param('PageNumber',PageNumber)