[![Build](https://github.com/jthomperoo/locust-pod-autoscaler/workflows/main/badge.svg)](https://github.com/jthomperoo/locust-pod-autoscaler/actions)
[![codecov](https://codecov.io/gh/jthomperoo/locust-pod-autoscaler/branch/master/graph/badge.svg)](https://codecov.io/gh/jthomperoo/locust-pod-autoscaler)
[![Documentation Status](https://readthedocs.org/projects/locust-pod-autoscaler/badge/?version=latest)](https://locust-pod-autoscaler.readthedocs.io/en/latest)
[![License](http://img.shields.io/:license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)
# Locust Pod Autoscaler

This is the Locust Pod Autoscaler, a Kubernetes Custom Pod Autoscaler that uses latency to scale.  

This is project is built using the [Custom Pod Autoscaler Framework](https://custom-pod-autoscaler.readthedocs.io/en/latest).  

## What is it?

This is a [Custom Pod Autoscaler](https://custom-pod-autoscaler.readthedocs.io/en/latest) for Kubernetes, powered by [Locust](https://locust.io/) to run load tests to retrieve latency statistics.  
This autoscaler allows you to write your own Locust tests to load test your Kubernetes applications, then provides simple configuration for scaling based on the results of these. For example an autoscaler could be created that gathers latency statistics every minute for a REST API, if the average latency goes above `50ms` then the application should be scaled up.

## How does it work?

The autoscaler works by running Locust tests you create in Python, then gathering the statistics from these before comparing with configured target latencies.  
Accompanying this upscaling based on latency is the idea of a *decay*, which can be configured as part of the autoscaler. The decay works by waiting for a number of runs of the autoscaler in which the number of replicas hasn't changed, and reducing the replica count by a configured amount. This allows flexiblity in conservatively or aggressively downscaling, and if it downscales too far the autoscaler will scale back up again based on latency tests.  

See the [example](https://github.com/jthomperoo/locust-pod-autoscaler/tree/master/example), or [getting started guide](user-guide/getting-started) for more information.
