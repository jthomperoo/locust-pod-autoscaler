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
from .evaluate import Evaluate

class FakeDecayHandler:
    def __init__(self, get_reactor, update_reactor):
        self.get_reactor = get_reactor
        self.update_reactor = update_reactor

    def get(self):
        return self.get_reactor()

    def update(self, decay_info):
        return self.update_reactor(decay_info)

def test_metric_get(subtests):
    test_cases = [
        {
            "description": "Missing results for target",
            "expected_exception": Exception("No results for target: GET_/test"),
            "decay_handler": None, 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "mean",
                        "target": 5
                    }
                ]
            }, 
            "run_type": "autoscaler",
            "metrics": {
                "requests": {}
            },
        },
        {
            "description": "Unknown target",
            "expected_exception": Exception("Unknown target type: invalid"),
            "decay_handler": None, 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "invalid",
                        "target": 5
                    }
                ]
            }, 
            "run_type": "autoscaler",
            "metrics": {
                "requests": {
                    "GET_/test": {}
                }
            },
        },
        {
            "description": "Fail to get decay info",
            "expected_exception": Exception("fail to get decay info"),
            "decay_handler": FakeDecayHandler(lambda: (_ for _ in ()).throw(Exception("fail to get decay info")), None), 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "mean",
                        "target": 5
                    }
                ],
                "decay": {
                    "replicas": 1,
                    "unchangedRuns": 4,
                }
            }, 
            "run_type": "autoscaler",
            "metrics": {
                "requests": {
                    "GET_/test": {
                        "avg_response_time": 4
                    }
                }
            },
        },
        {
            "description": "Fail to update decay info",
            "expected_exception": Exception("fail to update decay info"),
            "decay_handler": FakeDecayHandler(lambda: {"runs_since_change": 3}, 
                lambda decay_info: (_ for _ in ()).throw(Exception("fail to update decay info"))), 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "mean",
                        "target": 5
                    }
                ],
                "decay": {
                    "replicas": 1,
                    "unchangedRuns": 4,
                }
            }, 
            "run_type": "autoscaler",
            "metrics": {
                "requests": {
                    "GET_/test": {
                        "avg_response_time": 4
                    }
                }
            },
        },
        {
            "description": "3 targets, all under target, no decay",
            "expected": 2,
            "decay_handler": FakeDecayHandler(lambda: {"runs_since_change": 3}, lambda decay_info: None), 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "mean",
                        "target": 5
                    },
                    {
                        "method": "POST",
                        "endpoint": "/test2",
                        "type": "max",
                        "target": 6
                    },
                    {
                        "method": "DELETE",
                        "endpoint": "/test3",
                        "type": "median",
                        "target": 7
                    },
                ],
                "decay": {
                    "replicas": 1,
                    "unchangedRuns": 4,
                }
            }, 
            "run_type": "autoscaler",
            "metrics": {
                "current_replicas": 2,
                "requests": {
                    "GET_/test": {
                        "avg_response_time": 4
                    },
                    "POST_/test2": {
                        "max_response_time": 5
                    },
                    "DELETE_/test3": {
                        "median_response_time": 6
                    }
                }
            },
        },
        {
            "description": "3 targets, 2 under, 1 above, no decay",
            "expected": 3,
            "decay_handler": FakeDecayHandler(lambda: {"runs_since_change": 3}, lambda decay_info: None), 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "mean",
                        "target": 5
                    },
                    {
                        "method": "POST",
                        "endpoint": "/test2",
                        "type": "max",
                        "target": 6
                    },
                    {
                        "method": "DELETE",
                        "endpoint": "/test3",
                        "type": "median",
                        "target": 7
                    },
                ],
                "decay": {
                    "replicas": 1,
                    "unchangedRuns": 4,
                }
            }, 
            "run_type": "autoscaler",
            "metrics": {
                "current_replicas": 2,
                "requests": {
                    "GET_/test": {
                        "avg_response_time": 4
                    },
                    "POST_/test2": {
                        "max_response_time": 15
                    },
                    "DELETE_/test3": {
                        "median_response_time": 6
                    }
                }
            },
        },
        {
            "description": "3 targets, all under target, decay by 2",
            "expected": 8,
            "decay_handler": FakeDecayHandler(lambda: {"runs_since_change": 4}, lambda decay_info: None), 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "mean",
                        "target": 5
                    },
                    {
                        "method": "POST",
                        "endpoint": "/test2",
                        "type": "max",
                        "target": 6
                    },
                    {
                        "method": "DELETE",
                        "endpoint": "/test3",
                        "type": "median",
                        "target": 7
                    },
                ],
                "decay": {
                    "replicas": 2,
                    "unchangedRuns": 4,
                }
            }, 
            "run_type": "autoscaler",
            "metrics": {
                "current_replicas": 10,
                "requests": {
                    "GET_/test": {
                        "avg_response_time": 4
                    },
                    "POST_/test2": {
                        "max_response_time": 5
                    },
                    "DELETE_/test3": {
                        "median_response_time": 6
                    }
                }
            },
        },
                {
            "description": "3 targets, all under target, decay, dry run",
            "expected": 14,
            "decay_handler": FakeDecayHandler(lambda: {"runs_since_change": 4}, lambda decay_info: None), 
            "eval_config": {
                "targets": [
                    {
                        "method": "GET",
                        "endpoint": "/test",
                        "type": "mean",
                        "target": 5
                    },
                    {
                        "method": "POST",
                        "endpoint": "/test2",
                        "type": "max",
                        "target": 6
                    },
                    {
                        "method": "DELETE",
                        "endpoint": "/test3",
                        "type": "median",
                        "target": 7
                    },
                ],
                "decay": {
                    "replicas": 1,
                    "unchangedRuns": 2,
                }
            }, 
            "run_type": "api_dry_run",
            "metrics": {
                "current_replicas": 15,
                "requests": {
                    "GET_/test": {
                        "avg_response_time": 4
                    },
                    "POST_/test2": {
                        "max_response_time": 5
                    },
                    "DELETE_/test3": {
                        "median_response_time": 6
                    }
                }
            },
        },
    ]

    for i, test_case in enumerate(test_cases):
        with subtests.test(msg=test_case["description"], i=i):
            evaluator = Evaluate(test_case["decay_handler"], test_case["eval_config"], test_case["run_type"])
            if "expected_exception" in test_case.keys():
                with pytest.raises(type(test_case["expected_exception"])) as ex:
                    evaluator.get(test_case["metrics"])
                assert str(ex.value) == str(test_case["expected_exception"])
            else:
                assert test_case["expected"] == evaluator.get(test_case["metrics"])
