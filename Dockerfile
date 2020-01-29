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

# Pull in Python build of CPA
FROM custompodautoscaler/python:v0.10.0
# Add in python requirements to install dependencies
ADD requirements.txt /
# Install dependencies, done before adding Py files to allow Docker to cache better
RUN pip install -r /requirements.txt
# Add config and license
ADD config.yaml LICENSE /
# Add locust autoscaler source
ADD autoscaler /autoscaler