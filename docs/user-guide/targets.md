# Targets

Targets are the methods and endpoints that the autoscaler will load test, and values that the load test should target. If the load test results are above the targeted values the resources are scaled up.

Example:
```yaml
targets:
  - method: "GET"
    endpoint: "/fibonacci?n=10"
    type: "mean"
    target: 7
```

## Defining the target

The target is defined as a method and an endpoint, e.g. `GET /fibonacci?n=10`.

## Types
Targets define a type, which must be one of the following:

* `mean` - takes the mean average latency of the requests to the target, and compares it to the target value. If the mean average latency is above the target the resource is scaled up.
* `median` - takes the median average latency of the requests to the target, and compares it to the target value. If the median average latency is above the target the resource is scaled up.
* `max`- takes the maximum latency of the requests to the target, and compares it to the target value. If the maximum latency is above the target the resource is scaled up.