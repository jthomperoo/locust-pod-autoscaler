# Getting started
Developing a Locust Pod Autoscaler is designed to be simple and utilise the existing and mature Locust load testing framework.  

In this guide we will create a Locust Pod Autoscaler that will be responsible for scaling a Fibonacci calculating service.  
The Fibonacci service will expose an endpoint `/fibonacci` which accepts an integer query parameter `n` and returns the Fibonacci 
number at that position.  
For example `GET /fibonacci?n=7` would return `13`.  

The autoscaler will call this `/fibonacci` endpoint with the value `n=10` with `10` users for `5 seconds`. The latency values will
be collected and evaluated.  
The autoscaler will use these latency values to compare to an evaluation configuration, which will try to keep the mean latency
below `7 ms`.  
The autoscaler will use a decay, causing the replica count to be reduced by `1` replica every `3` runs in which there is no 
scaling change.  

The finished and full code 
[can be found in the example in the locust-pod-autoscaler repository](https://github.com/jthomperoo/locust-pod-autoscaler/tree/master/example).

## Set up the development environment

Dependencies required to follow this guide:

* [Python 3](https://www.python.org/downloads/)
* [Docker](https://docs.docker.com/install/)
* [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) or another Kubernetes cluster
* [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## Enable Custom Pod Autoscalers on your cluster

Using this Locust Autoscaler requires Custom Pod Autoscalers (CPAs) to be enabled on your kubernetes cluster, [follow this guide to set up CPAs on your cluster](https://github.com/jthomperoo/custom-pod-autoscaler-operator#installation).  

## Create the project

Create a new directory for the project `locust-example-autoscaler` and begin working out the project 
directory.
```
mkdir locust-example-autoscaler
```

## Create the Fibonacci application
Create an `app` folder.  
Create the following files inside the `app` folder:  
`api.py`:
```python
from flask import Flask, abort, request
import json
app = Flask(__name__)

@app.route("/fibonacci")
def fibonacci_endpoint():
    nVal = request.args.get("n")
    try:
        n = int(nVal)
        return str(fibonacci(n))
    except ValueError:
        abort(400, f"Value '{nVal}' is not an integer")

def fibonacci(n): 
    # First Fibonacci number is 0 
    if n==1: 
        return 0
    # Second Fibonacci number is 1 
    elif n==2: 
        return 1
    else: 
        return fibonacci(n-1)+fibonacci(n-2) 

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
```
`Dockerfile`:
```Dockerfile
FROM python:3.6-slim
# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
# Install dependencies
RUN pip install -r requirements.txt
# Copy in source files
COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "api.py" ]
```
`requirements.txt`:
```
Flask==1.0
```
`deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fibonacci
  labels:
    app: fibonacci
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fibonacci
  template:
    metadata:
      labels:
        app: fibonacci
    spec:
      containers:
      - name: fibonacci
        image: fibonacci:latest
        ports:
        - containerPort: 5000
        imagePullPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: fibonacci
spec:
  ports:
  - port: 5000
    protocol: TCP
    targetPort: 5000
  selector:
    app: fibonacci
  type: ClusterIP
```

## Build and deploy the Fibonacci application

* Switch to the Minikube Docker registry:  
`eval $(minikube docker-env)`
* Inside the `app` folder build the Docker image of the application:  
`docker build -t fibonacci .`
* Deploy the application using `kubectl`:  
`kubectl apply -f deployment.yaml`

## Write the Locust test

Now we have an application running we can manage, lets write our load test in Python using Locust:
```python
from locust import HttpLocust, TaskSet, task, between

class UserBehavior(TaskSet):
    @task(1)
    def profile(self):
        self.client.get("/fibonacci?n=10")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    wait_time = between(5, 9)
```
This simple Locust test will call the `GET /fibonacci?n=10` endpoint.

## Write the evaluation configuration

Lets write our evaluation configuration:
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
This configuration is in two parts; `targets` and `decay`.  
The `targets` configuration defines the `GET /fibonacci?n=10` endpoint, and states that the result mean average latency should be kept below `7ms`.  
The `decay` configuration defines that the decay will occur every `3` runs without scaling change, and the replica count will be reduced by `1`.

## Write the Dockerfile

Lets pull the code we have written together into a Docker image with our Dockerfile:
```Dockerfile
FROM jthomperoo/locust-pod-autoscaler:latest

ENV locustFilePath=/locustfile.py evaluationConfigFilePath=/evaluation_config.yaml

ENV locustRunTime=5 locustUsers=10 locustHatchRate=10

ADD locustfile.py evaluation_config.yaml /
```

This Dockerfile:  
* Sets file paths of Locust test file and the evaluation configuration.
* Sets some Locust values; the load testing will run for `5 seconds`, with `10` users that are spawned at a rate of `10` a second.
* Adds in locust file and evaluation configuration we have created.

## Write the deployment YAML

Now we have our Docker image and all our autoscaler created, we just need to create a deployment file for the autoscaler:
```yaml
apiVersion: custompodautoscaler.com/v1alpha1
kind: CustomPodAutoscaler
metadata:
  name: locust-autoscaler-example
spec:
  template:
    spec:
      containers:
      - name: locust-autoscaler-example
        image: locust-pod-autoscaler-example:latest
        imagePullPolicy: Always
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fibonacci
  config: 
    - name: interval
      value: "10000"
    - name: locustHost
      value: "http://fibonacci:5000"
```

This YAML outlines the name of our autoscaler instance, the image/pod definition for our autoscaler using `template`, 
the resource we are targeting to manage using `scaleTargetRef` and some basic extra configuration with interval set to `10000 milliseconds`, 
meaning the autoscaler will run every `10 seconds` and the `locustHost` defined as `http://fibonacci:5000`.

## Build and deploy the autoscaler

* Target the Minikube registry for building the image:  
`eval $(minikube docker-env)`
* Build the example image.  
`docker build -t locust-pod-autoscaler-example .`  
* Deploy the Locust Autoscaler using the image just built.  
`kubectl apply -f locust_autoscaler.yaml`  
Now the Locust Autoscaler should be running on your cluster, managing the app we previously deployed.

## Test the autoscaler

Watch the autoscaler's logs with:  
```
kubectl logs locust-autoscaler-example --follow
```

Increase the load with:  
```
kubectl run --generator=run-pod/v1 -it --rm load-generator --image=busybox /bin/sh
```
Once a prompt appears:  
```
while true; do wget -q -O- http://fibonacci:5000/fibonacci?n=23; done
```
This will repeatedly call the fibonacci service with the value `23`; this should increase load and the number of replicas should increase.  
Once the replica count increases, try stopping the increased load and check the decay works, it should wait for `3` unchanged load tests before scaling down by `1`, it should repeat this until it reaches a stable state.

## Clean up

Run these commands to remove any resources created during this guide:
```
kubectl delete -f app/deployment.yaml
```
Removes our managed deployment.

```
kubectl delete -f locust_autoscaler.yaml
```
Removes our autoscaler.

```
VERSION=v0.5.0
curl -L "https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/${VERSION}/cluster.tar.gz" | tar xvz --to-command 'kubectl delete -f -'
```
Removes the Custom Pod Autoscaler operator.

## Conclusion

Congratulations! You have now successfully created a Locust Pod Autoscaler.