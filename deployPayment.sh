#!/bin/bash

# Start Minikube
minikube start

# Point Docker client to the Docker daemon inside Minikube
eval $(minikube -p minikube docker-env)

# Build the Docker image
docker build -t payment-microservice .

# Create a Kubernetes deployment using the YAML file
kubectl apply -f service.yaml

# Wait for the deployment to be ready
kubectl rollout status deployment/payment-deployment

echo "Deployment complete! Access the service at the following URL:"
minikube service payment-microservice-service