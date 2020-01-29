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
Decay handles interactions with the decay info file, for storing decay
information such as number of runs since a scaling change
"""
import json

class DecayHandler:
    """
    DecayHandler abstracts interactions with the file system to get
    and update the decay info file
    """
    def __init__(self, decay_file):
        self.decay_file = decay_file

    def get(self):
        """
        get returns the decay info parsed into a JSON dict
        """
        # if empty, create a new JSON decay info
        self.decay_file.seek(0)
        data = self.decay_file.read()
        if data == "":
            return {
                "runs_since_change": 0
            }
        return json.loads(data)

    def update(self, decay_info):
        """
        update writes the provided decay_info to the decay info file
        """
        self.decay_file.seek(0)
        self.decay_file.write(json.dumps(decay_info))
