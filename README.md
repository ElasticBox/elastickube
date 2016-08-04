## ElasticKube - The Kubernetes Management Platform

ElasticKube is an open source management platform for Kubernetes with the goal of providing a self-service experience for containerized applications.


### Designed for Kubernetes

Kubernetes (https://github.com/kubernetes/kubernetes) is ready to serve your production workloads. ElasticKube provides the processes to manage Kubernetes workloads for complex organizations.

We designed ElasticKube with the following principles in mind:

* **non opinionated**: unrestricted kubernetes experience
* **standardized**: works in any kubernetes cluster
* **stateless**: lifecycle and state is always stored in kubernetes
* **integrated**: git, jenkins, sso authentication


### Getting started

ElastiKube runs as a containerized application inside your Kubernetes cluster. To deploy ElasticKube the only requirement is access to a terminal with `kubectl` configured.

To install ElasticKube you can execute the [build/deploy.sh](../master/build/deploy.sh) deployment script, or execute the following command from the command line:

  `curl -s https://elastickube.com | bash`

If you cluster kube-system namespace does not have a kubernetes service and a service account use the unsecure url by adding the `-u` parameter:

  `curl -s https://elastickube.com | bash -s -- -u http://<kube-apiserver>:8080`

For example the default Azure scripts name the kube-api server 'kube-00', to deploy in such environment use the following command:

  `curl -s https://elastickube.com | bash -s -- -u http://kube-00:8080`

Once ElasticKube is installed, please complete the onboarding process using the load balancer IP address produced by the installation script.
