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

import pytest
from .metric import Metric

class FakeLoadTest:
    def __init__(self, run_reactor, stats_reactor):
        self.run_reactor = run_reactor
        self.stats_reactor = stats_reactor

    def run(self):
        return self.run_reactor()

    def stats(self):
        return self.stats_reactor()


def test_metric_get(subtests):
    test_cases = [
        {
            "description": "Fail to run tests",
            "expected_exception": Exception("fail to run tests"),
            "resource": {
                "spec": {
                    "replicas": 3
                }
            },
            "load_test": FakeLoadTest(lambda: (_ for _ in ()).throw(Exception("fail to run tests")), None)
        },
        {
            "description": "Fail to get stats",
            "expected_exception": Exception("fail to get stats"),
            "resource": {
                "spec": {
                    "replicas": 3
                }
            },
            "load_test": FakeLoadTest(lambda: None, lambda: (_ for _ in ()).throw(Exception("fail to get stats")))
        },
        {
            "description": "Success get results",
            "expected": {
                "current_replicas": 3,
                "success": True
            },
            "resource": {
                "spec": {
                    "replicas": 3
                }
            },
            "load_test": FakeLoadTest(lambda: None, lambda: {
                "success": True
            })
        },
    ]

    for i, test_case in enumerate(test_cases):
        with subtests.test(msg=test_case["description"], i=i):
            metric_gatherer = Metric(test_case["load_test"])
            if "expected_exception" in test_case.keys():
                with pytest.raises(type(test_case["expected_exception"])) as ex:
                    metric_gatherer.get(test_case["resource"])
                assert str(ex.value) == str(test_case["expected_exception"])
            else:
                assert test_case["expected"] == metric_gatherer.get(test_case["resource"])
