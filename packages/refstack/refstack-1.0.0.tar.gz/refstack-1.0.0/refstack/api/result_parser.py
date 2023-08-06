#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from refstack.api.controllers import capabilities
from refstack import db

class ResultParser:
	
	def __init__(self, guideline, target_program, test_id):
		self.guideline = guideline
		self.target_program = target_program
		self.test_id = test_id
		
	def get_guidelines(self):
		capController = capabilities.CapabilitiesController()
		try:
			resp = capController.get_specific_capability_file(self.guideline)
			if response.status_code == 200:
                return response.json()
            else:
                LOG.warning('Github returned non-success HTTP '
                            'code: %s' % response.status_code)
                pecan.abort(response.status_code)
        except requests.exceptions.RequestException as e:
            LOG.warning('An error occurred trying to get GitHub '
                        'capability file contents: %s' % e)
            pecan.abort(500)

    def get_passed_tests(self):
		return db.get_test_results(self.test_id)
		
	def get_plat
	
	def check_compliance(self):
		guidelines = self.get_guidelines()
		passed_list = self.get_passed_tests()
		
		
		
