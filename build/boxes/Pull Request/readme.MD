# Overview

This box installs a fully functional Kubernetes system including the following basic services:

- SKYDNS
- KubeUI (comming soon)

## MongoDB

Mongo is hosted in a resource controller called `elastickube-mongo` on the `kube-system` namespaces. The pod exposes the mongo port using the host port.

Mongo tools are also installed in the host as part of the setup process. Usage:

    mongo admin