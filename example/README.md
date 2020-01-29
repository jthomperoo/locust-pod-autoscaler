# Locust Autoscaler example
This example shows how to use the Locust Autoscaler, with user supplied Python test files.  
The example extends the Locust Autoscaler base image (jthomperoo/locustautoscaler) and adds in locust test files.
The code is verbosely commented and designed to be read and understood for building your own Locust Autoscalers.
See [the getting started guide for a full explaination of this example](https://custom-pod-autoscaler.readthedocs.io/en/latest/user-guide/getting-started).  

## Overview
This example contains a docker image of the example Locust Autoscaler, alongside using the `fibonacci` sample application as a target to scale up and down in the `app` directory.

### Example Locust Autoscaler

## Usage
Trying out this example requires a kubernetes cluster to try it out on, this guide will assume you are using Minikube.  

### Enable CPAs
Using this Locust Autoscaler requires Custom Pod Autoscalers (CPAs) to be enabled on your kubernetes cluster, [follow this guide to set up CPAs on your cluster](https://github.com/jthomperoo/custom-pod-autoscaler-operator#installation).  

### Switch to target the Minikube registry
Target the Minikube registry for building the image:  
`eval $(minikube docker-env)`

### Deploy the fibonacci app to manage
You need to deploy an app for the Locust Autoscaler to manage:  
* Build the example app image.  
`docker build -t fibonacci ./app`  
* Deploy the app using a deployment.  
`kubectl apply -f ./app/deployment.yaml`  
Now you have an app running to manage scaling for.

### Build Locust Autoscaling image
Once CPAs have been enabled on your cluster, you need to build this example, run these commands to build the example:  
* Build the example image.  
`docker build -t locust-pod-autoscaler-example .`  
* Deploy the Locust Autoscaler using the image just built.  
`kubectl apply -f locust_autoscaler.yaml`  
Now the Locust Autoscaler should be running on your cluster, managing the app we previously deployed.
