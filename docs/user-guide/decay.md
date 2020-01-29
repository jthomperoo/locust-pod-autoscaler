# Decay

Decay is the mechanism for scaling down, as if an application has too many resources and has been over provisioned the latency will not neccessarily reflect this, as it may have the same minimum latency for 1 pod and 100 pods.  

Decay works by waiting for the autoscaler to run a number of times without scaling up, and at this point the autoscaler will use a decay to reduce the number of replicas by a configured amount. This allows a flexible scale down strategy, which can be conservative or aggressive. If aggressively scaling down with a frequent decay, if downscaling too far the autoscaler will simply rectify this with its next load test and scale back up to the required levels.

Example:
```yaml
decay: 
  replicas: 1
  unchangedRuns: 3
```

## Replicas

This is how many replicas to decay by for a decay, for example a `replicas` value of `5` would result in a scale down of `5` pods on a decay.

## Unchanged Runs

This is how many times the autoscaler should be run without any scaling up or down before doing a decay. For example a value of `6` would make the autoscaler wait for `6` runs of the load tester without any scale change before decaying. Decaying itself counts as a scale change, so after a decay it would wait a minimum of `6` more runs before scaling down again.