# Evaluation Configuration

The evaluation logic can be configured through YAML that specifies latency targets and decay information.

## How to provide configuration
### Configuration file
Example:
```yaml
targets:
  - method: "GET"
    endpoint: "/fibonacci?n=10"
    type: "mean"
    target: 7
decay: 
  replicas: 1
  unchangedRuns: 3
```

This configuration can be baked into the Docker image to provide a standard configuration for the autoscaler.

## targets
Example:
```yaml
targets:
  - method: "GET"
    endpoint: "/fibonacci?n=10"
    type: "mean"
    target: 7
```

A list of methods and endpoints, and their targeted latencies. See the [targets page for more information](../../user-guide/targets).

## decay
Example:
```yaml
decay: 
  replicas: 1
  unchangedRuns: 3
```

A decay that will occur when changes do not occur to replica counts. See the [decay page for more information](../../user-guide/decay).  

