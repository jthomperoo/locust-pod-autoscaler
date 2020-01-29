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
Entrypoint for the locust autoscaler, routes to required logic
based on mode provided, gathers environment variables and reads
stdin
"""
import os
import sys
import json
import argparse
import yaml
import invokust

from metric.metric import Metric
from evaluate.evaluate import Evaluate
from decay.decay import DecayHandler

METRIC_MODE = "metric"
EVALUATE_MODE = "evaluate"

def main():
    """
    Main method for locust autoscaler, routes based on specified mode
    """
    # get mode
    parser = argparse.ArgumentParser()
    parser.add_argument("mode")
    args = parser.parse_args()

    # determine evaluation or metric based on mode
    if args.mode == METRIC_MODE:
        gather_metric()
    elif args.mode == EVALUATE_MODE:
        gather_evaluation()
    else:
        sys.stderr.write(f"Unknown mode: {args.mode}")
        sys.exit(1)

def gather_metric():
    """
    gather_metrics retrieves environment variables and feeds them
    into the metric gathering logic, outputting the results to
    stdout
    """
    # get k8s resource
    resource = json.loads(sys.stdin.read())

    # get env vars
    host = os.getenv("locustHost", default=None)
    run_time = os.getenv("locustRunTime", default="20")
    file_path = os.getenv("locustFilePath", default="/locustfile.py")
    try:
        user_count = int(os.getenv("locustUsers", default=None))
        hatch_rate = int(os.getenv("locustHatchRate", default=None))
    except ValueError as err:
        sys.stderr.write(f"Error parsing locust settings: {str(err)}")
        sys.exit(1)

    # set up locust
    settings = invokust.create_settings(
        locustfile=file_path,
        host=host,
        num_clients=user_count,
        hatch_rate=hatch_rate,
        run_time=run_time
    )
    load_test = invokust.LocustLoadTest(settings)

    # set up metric gatherer
    metric_gatherer = Metric(load_test)
    # get metric
    result = metric_gatherer.get(resource)
    # write to stdout
    sys.stdout.write((json.dumps(result)))


def gather_evaluation():
    """
    gather_evaluation retrieves stdin and feeds it to the evaluation
    logic, outputting the results to stdout
    """

    # get evaluation config
    eval_config_file_path = os.getenv("evaluationConfigFilePath", default="/evaluation_config.yaml")
    eval_config = None
    with open(eval_config_file_path, "r") as eval_config_file:
        # parse YAML into dict
        eval_config = yaml.load(eval_config_file, Loader=yaml.FullLoader)

    # get provided metrics
    resource_metrics = json.loads(sys.stdin.read())
    metrics = resource_metrics.get("metrics")
    metric = metrics[0]
    metric_value = json.loads(metric.get("value"))
    run_type = resource_metrics.get("run_type")

    # open decay info file
    decay_info_file_path = os.getenv("decayInfoFilePath", default="/decay_info.json")
    # create empty file if doesn't exist
    open(decay_info_file_path, "a").close()
    # open file in read-write mode
    with open(decay_info_file_path, "r+") as decay_info_file:
        # set up decay handler
        decay_handler = DecayHandler(decay_info_file)

        # set up evaluator and get evaluation
        evaluater = Evaluate(decay_handler, eval_config, run_type)
        result = evaluater.get(metric_value)
        sys.stdout.write((json.dumps({
            "target_replicas": result
        })))

if __name__ == "__main__":
    main()
