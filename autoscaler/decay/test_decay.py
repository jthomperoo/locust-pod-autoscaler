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
from .decay import DecayHandler

class FakeDecayFile:
    def __init__(self, seek_reactor, read_reactor, write_reactor):
        self.seek_reactor = seek_reactor
        self.read_reactor = read_reactor
        self.write_reactor = write_reactor

    def seek(self, pos):
        return self.seek_reactor(pos)

    def read(self):
        return self.read_reactor()

    def write(self, data):
        return self.write_reactor(data)

def test_decay_get(subtests):
    test_cases = [
        {
            "description": "Fail to seek",
            "expected_exception": Exception("fail to seek"),
            "decay_file": FakeDecayFile(lambda pos: (_ for _ in ()).throw(Exception("fail to seek")), None, None),
        },
        {
            "description": "Fail to read",
            "expected_exception": Exception("fail to read"),
            "decay_file": FakeDecayFile(lambda pos: None, lambda: (_ for _ in ()).throw(Exception("fail to read")), None),
        },
        {
            "description": "Empty file, return starter JSON",
            "expected": {
                "runs_since_change": 0
            },
            "decay_file": FakeDecayFile(lambda pos: None, lambda: "", None),
        },
        {
            "description": "Success",
            "expected": {
                "runs_since_change": 3
            },
            "decay_file": FakeDecayFile(lambda pos: None, lambda: "{\"runs_since_change\": 3}", None),
        }
    ]

    for i, test_case in enumerate(test_cases):
        with subtests.test(msg=test_case["description"], i=i):
            decay_handler = DecayHandler(test_case["decay_file"])
            if "expected_exception" in test_case.keys():
                with pytest.raises(type(test_case["expected_exception"])) as ex:
                    decay_handler.get()
                assert str(ex.value) == str(test_case["expected_exception"])
            else:
                assert test_case["expected"] == decay_handler.get()

def test_decay_update(subtests):
    test_cases = [
        {
            "description": "Fail to seek",
            "expected_exception": Exception("fail to seek"),
            "decay_info": {
                "runs_since_change": 1
            },
            "decay_file": FakeDecayFile(lambda pos: (_ for _ in ()).throw(Exception("fail to seek")), None, None),
        },
        {
            "description": "Fail to write",
            "expected_exception": Exception("fail to write"),
            "decay_info": {
                "runs_since_change": 1
            },
            "decay_file": FakeDecayFile(lambda pos: None, None, lambda data: (_ for _ in ()).throw(Exception("fail to write"))),
        },
        {
            "description": "Success",
            "expected": None,
            "decay_info": {
                "runs_since_change": 3
            },
            "decay_file": FakeDecayFile(lambda pos: None, None, lambda data: None),
        }
    ]

    for i, test_case in enumerate(test_cases):
        with subtests.test(msg=test_case["description"], i=i):
            decay_handler = DecayHandler(test_case["decay_file"])
            if "expected_exception" in test_case.keys():
                with pytest.raises(type(test_case["expected_exception"])) as ex:
                    decay_handler.update(test_case["decay_info"])
                assert str(ex.value) == str(test_case["expected_exception"])
            else:
                assert test_case["expected"] == decay_handler.update(test_case["decay_info"])