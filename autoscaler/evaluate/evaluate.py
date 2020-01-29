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
Evaluate handles calculating the number of replicas a resource should have,
based on the locust metric results and targets provided
"""

TARGET_MEAN = "mean"
TARGET_MEDIAN = "median"
TARGET_MAX = "max"

class Evaluate:
    """
    Evaluate abstracts calculating an evaluation, handling comparing
    targets with requests and determining decay
    """
    def __init__(self, decay_handler, eval_config, run_type):
        self.decay_handler = decay_handler
        self.eval_config = eval_config
        self.run_type = run_type

    def get(self, metrics):
        """
        get handles comparing targets and locust results and scaling
        as needed
        """
        current_replicas = metrics.get("current_replicas")

        target_replica_count = self.__determine_target(metrics)
        target_replica_count = self.__determine_decay(target_replica_count, current_replicas)

        return target_replica_count

    def __determine_target(self, metrics):
        requests = metrics.get("requests")
        targets = self.eval_config.get("targets")

        current_replicas = metrics.get("current_replicas")
        target_replica_count = current_replicas

        # Iterate through targets, for each one compare target with results,
        # if target below result, set target replicas to current replicas + 1
        for target in targets:
            # get target values
            target_method = target.get("method")
            target_endpoint = target.get("endpoint")
            target_type = target.get("type")
            target_value = target.get("target")

            # build request name, check if target matches a request
            target_name = f"{target_method}_{target_endpoint}"
            if target_name not in requests:
                raise Exception(f"No results for target: {target_name}")

            # get matching request
            request = requests.get(target_name)
            result_value = None
            if target_type == TARGET_MEAN:
                result_value = request.get("avg_response_time")
            elif target_type == TARGET_MEDIAN:
                result_value = request.get("median_response_time")
            elif target_type == TARGET_MAX:
                result_value = request.get("max_response_time")
            else:
                raise Exception(f"Unknown target type: {target_type}")

            if result_value > target_value:
                target_replica_count = current_replicas + 1
        return target_replica_count

    def __determine_decay(self, target_replica_count, current_replicas):
        # get decay config
        decay_config = self.eval_config.get("decay")
        decay_replicas = decay_config.get("replicas")
        decay_unchanged_runs = int(decay_config.get("unchangedRuns"))

        # get decay info
        decay_info = self.decay_handler.get()
        runs_since_change = int(decay_info["runs_since_change"])

        # if unchanged replica count, check for decay conditions
        if target_replica_count == current_replicas:
            if runs_since_change >= decay_unchanged_runs:
                # enough runs have passed without change, decay by configured amount
                target_replica_count = current_replicas - decay_replicas

        if self.run_type != "api_dry_run":
            if target_replica_count == current_replicas:
                # replica count unchanged, increment runs since change
                decay_info["runs_since_change"] = runs_since_change + 1
            else:
                # replica count changed, reset runs since change
                decay_info["runs_since_change"] = 0
            self.decay_handler.update(decay_info)
        return target_replica_count
