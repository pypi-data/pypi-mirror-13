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

from aliyunsdkcore.request import RpcRequest
class ImportImageRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Ecs', '2014-05-26', 'ImportImage')

	def get_OwnerId(self):
		return self.get_query_params().get('OwnerId')

	def set_OwnerId(self,OwnerId):
		self.add_query_param('OwnerId',OwnerId)

	def get_ResourceOwnerAccount(self):
		return self.get_query_params().get('ResourceOwnerAccount')

	def set_ResourceOwnerAccount(self,ResourceOwnerAccount):
		self.add_query_param('ResourceOwnerAccount',ResourceOwnerAccount)

	def get_ResourceOwnerId(self):
		return self.get_query_params().get('ResourceOwnerId')

	def set_ResourceOwnerId(self,ResourceOwnerId):
		self.add_query_param('ResourceOwnerId',ResourceOwnerId)

	def get_ImageName(self):
		return self.get_query_params().get('ImageName')

	def set_ImageName(self,ImageName):
		self.add_query_param('ImageName',ImageName)

	def get_Description(self):
		return self.get_query_params().get('Description')

	def set_Description(self,Description):
		self.add_query_param('Description',Description)

	def get_Architecture(self):
		return self.get_query_params().get('Architecture')

	def set_Architecture(self,Architecture):
		self.add_query_param('Architecture',Architecture)

	def get_OSType(self):
		return self.get_query_params().get('OSType')

	def set_OSType(self,OSType):
		self.add_query_param('OSType',OSType)

	def get_Platform(self):
		return self.get_query_params().get('Platform')

	def set_Platform(self,Platform):
		self.add_query_param('Platform',Platform)

	def get_DiskDeviceMapping1Format(self):
		return self.get_query_params().get('DiskDeviceMapping.1.Format')

	def set_DiskDeviceMapping1Format(self,DiskDeviceMapping1Format):
		self.add_query_param('DiskDeviceMapping.1.Format',DiskDeviceMapping1Format)

	def get_DiskDeviceMapping1OSSBucket(self):
		return self.get_query_params().get('DiskDeviceMapping.1.OSSBucket')

	def set_DiskDeviceMapping1OSSBucket(self,DiskDeviceMapping1OSSBucket):
		self.add_query_param('DiskDeviceMapping.1.OSSBucket',DiskDeviceMapping1OSSBucket)

	def get_DiskDeviceMapping1OSSObject(self):
		return self.get_query_params().get('DiskDeviceMapping.1.OSSObject')

	def set_DiskDeviceMapping1OSSObject(self,DiskDeviceMapping1OSSObject):
		self.add_query_param('DiskDeviceMapping.1.OSSObject',DiskDeviceMapping1OSSObject)

	def get_DiskDeviceMapping1DiskImSize(self):
		return self.get_query_params().get('DiskDeviceMapping.1.DiskImSize')

	def set_DiskDeviceMapping1DiskImSize(self,DiskDeviceMapping1DiskImSize):
		self.add_query_param('DiskDeviceMapping.1.DiskImSize',DiskDeviceMapping1DiskImSize)

	def get_DiskDeviceMapping1Device(self):
		return self.get_query_params().get('DiskDeviceMapping.1.Device')

	def set_DiskDeviceMapping1Device(self,DiskDeviceMapping1Device):
		self.add_query_param('DiskDeviceMapping.1.Device',DiskDeviceMapping1Device)

	def get_RoleName(self):
		return self.get_query_params().get('RoleName')

	def set_RoleName(self,RoleName):
		self.add_query_param('RoleName',RoleName)