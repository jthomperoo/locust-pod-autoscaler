# Copyright 2020 Locust Pod Autoscaler Authors.
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
"""
Metric handles starting the locust load tester, retrieving results from it,
and parsing current replica count from the k8s resource before returning
it
"""

class Metric:
    """
    Metric abstracts retrieving metrics by running the locust load testing
    and returning the results, alongside the current replica count
    """
    def __init__(self, load_test):
        self.load_test = load_test

    def get(self, resource):
        """
        get handles running the locust autoscaler and returning the
        results
        """
        # run tests
        self.load_test.run()
        # get results
        results = self.load_test.stats()
        # add current replica count from resource definition
        current_replicas = int(resource.get("spec").get("replicas"))
        results["current_replicas"] = current_replicas
        return results
