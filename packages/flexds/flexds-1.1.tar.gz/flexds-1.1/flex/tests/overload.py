"""
Copyright 2016 Derek Ruths

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import unittest
from flex.pipeline import get_pipeline, USE_FILE_PREFIX
import flex.pipeline as pipeline
import os, os.path

BASE_PATH = os.path.dirname(__file__)

def get_complete_filename(fname):
	return os.path.join(BASE_PATH,'pipelines',fname)

class OverloadTestCase(unittest.TestCase):
	
	def test_overload1(self):
		
		p = get_pipeline(get_complete_filename('overload1'),default_prefix=USE_FILE_PREFIX)
		p.unmark_all_tasks()
		p.run()

		self.assertTrue(os.path.exists(get_complete_filename('overload1_2.txt')))

		os.remove(get_complete_filename('overload1_2.txt'))

