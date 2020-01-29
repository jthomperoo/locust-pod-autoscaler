# Autoscaler Configuration

The Autoscaler can be configured through environment variables, defined in the autoscaler deployment YAML or in the Dockerfile for the autoscaler.

## How to provide configuration
### Dockerfile
Example:
```Dockerfile
ENV locustFilePath=/locustfile.py evaluationConfigFilePath=/evaluation_config.yaml
```

This configuration can be baked into the Docker image to provide a standard configuration for the autoscaler.

### Deployment YAML
Example:
```yaml
  config: 
    - name: locustHost
      value: "http://fibonacci:5000"
    - name: locustUsers
      value: "10"
```

This configuration can be modified at deploy time rather than baked in at build time, allowing more fine tuned customisation.

## locustHost
```yaml
  config: 
    - name: locustHost
      value: "http://fibonacci:5000"
```
**Required** - no default.  
This defines the host of the service to load test for latency, required.

## locustRunTime
```yaml
  config: 
    - name: locustRunTime
      value: "50"
```
Default: `20`
This defines how long the load tester will run to gather latency statistics.

## locustFilePath
```yaml
  config: 
    - name: locustFilePath
      value: "/locustfiles/locustfile.py"
```
Default: `/locustfile.py`
Defines where the Locust Python file is that should be run for the load test.

## locustUsers
```yaml
  config: 
    - name: locustUsers
      value: "15"
```
**Required** - no default.  
The number of users for Locust to create for load testing

## locustHatchRate
```yaml
  config: 
    - name: locustHatchRate
      value: "5"
```
**Required** - no default.  
The rate at which users should be created by Locust.

## evaluationConfigFilePath
```yaml
  config: 
    - name: evaluationConfigFilePath
      value: "/config/eval_config.yaml"
```
Default: `/evaluation_config.yaml"` 
The file path of the evaluation configuration YAML.

## decayInfoFilePath
```yaml
  config: 
    - name: decayInfoFilePath
      value: "/decay/decay.json"
```
Default: `/decay_info.json` 
The file path to put the decay information, has to be readable and writeable.
