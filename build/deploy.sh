#!/bin/bash

USAGE="Usage :  deploy.sh [options]

Example:
    deploy.sh -t 600

Options:
    -t Timeout in seconds per operation
    -u Master Kubernetes URL
    -v ElasticKube version to install
    -h Display this message
"

function help() {
    echo "${USAGE}"

    if [[ ${1} ]]
    then
        echo ${1}
    fi
}

# Handle options
while getopts ":t:u:v:hr" ARGUMENT
do
  case ${ARGUMENT} in

    t )  export TIMEOUT=$OPTARG;;
    r )  export REINSTALL=true;;
    u )  export KUBERNETES_SERVICE_HOST=$OPTARG;;
    v )  export ELASTICKUBE_VERSION=$OPTARG;;
    h )  help; exit 0;;
    : )  help "Missing option argument for -$OPTARG."; exit 1;;
    \?)  help "Option does not exist : $OPTARG."; exit 1;;

  esac
done

# Default timeout
TIMEOUT=${TIMEOUT:-600}

# DEFAULT VERSION SECTION
VERSION=${ELASTICKUBE_VERSION:-latest}
# DEFAULT VERSION SECTION

if [ "${KUBERNETES_SERVICE_HOST}" ]
then

MASTER_URL_ENV_SECTION="
        env:
        - name: KUBERNETES_SERVICE_HOST
          value: ${KUBERNETES_SERVICE_HOST}
"

fi

cat << \
'______________________________HEADER______________________________'
  _____ _           _   _      _  __     _
 | ____| | __ _ ___| |_(_) ___| |/ /   _| |__   ___
 |  _| | |/ _` / __| __| |/ __| ' / | | | '_ \ / _ \
 | |___| | (_| \__ \ |_| | (__| . \ |_| | |_) |  __/
 |_____|_|\__,_|___/\__|_|\___|_|\_\__,_|_.__/ \___| by ElasticBox

______________________________HEADER______________________________

PROGRESS_WIDTH=40

ELASTICKUBE_MONGO_RC="
apiVersion: v1
kind: ReplicationController
metadata:
  name: elastickube-mongo
  namespace: kube-system
  labels:
    name: elastickube-mongo
spec:
  replicas: 1
  selector:
    name: elastickube-mongo
  template:
    metadata:
      labels:
        name: elastickube-mongo
    spec:
      containers:
        - image: mongo
          name: elastickube-mongo
          args:
          - --replSet=elastickube
          ports:
          - name: mongo
            containerPort: 27017
            hostPort: 27017
          volumeMounts:
            - name: mongo-persistent-storage
              mountPath: /data/mongodb
      volumes:
      - name: mongo-persistent-storage
        hostPath:
          path: /data/mongodb
"


ELASTICKUBE_MONGO_SVC="
apiVersion: v1
kind: Service
metadata:
  name: elastickube-mongo
  namespace: kube-system
  labels:
    name: elastickube-mongo
spec:
  ports:
    - port: 27017
      targetPort: 27017
  selector:
    name: elastickube-mongo
"

ELASTICKUBE_SERVER_RC="
apiVersion: v1
kind: ReplicationController
metadata:
  name: elastickube-server
  namespace: kube-system
  labels:
    name: elastickube-server
spec:
  replicas: 1
  selector:
    name: elastickube-server
  template:
    metadata:
      labels:
        name: elastickube-server
    spec:
      containers:
      - name: elastickube-api
        image: elasticbox/elastickube-api:${VERSION}
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
        volumeMounts:
        - name: elastickube-run
          mountPath: /var/run
${MASTER_URL_ENV_SECTION}
      - name: elastickube-charts
        image: elasticbox/elastickube-charts:${VERSION}
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
        volumeMounts:
        - name: elastickube-charts
          mountPath: /var/elastickube/charts
      - name: elastickube-nginx
        image: elasticbox/elastickube-nginx:${VERSION}
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
        volumeMounts:
        - name: elastickube-run
          mountPath: /var/run
        ports:
        - containerPort: 80
          hostPort: 80
          name: http
          protocol: TCP
      - name: elastickube-diagnostics
        image: elasticbox/elastickube-diagnostics:${VERSION}
        resources:
          limits:
            cpu: 10m
            memory: 32Mi
        volumeMounts:
        - name: elastickube-run
          mountPath: /var/run
      - name: elastickube-notifications
        image: elasticbox/elastickube-notifications:${VERSION}
        resources:
          limits:
            cpu: 10m
            memory: 32Mi
        volumeMounts:
        - name: elastickube-run
          mountPath: /var/run
      volumes:
      - name: elastickube-charts
        hostPath:
          path: /var/elastickube/charts
      - name: elastickube-run
        hostPath:
          path: /var/run/elastickube
"

ELASTICKUBE_SERVER_SVC="
apiVersion: v1
kind: Service
metadata:
  name: elastickube-server
  namespace: kube-system
  labels:
    name: elastickube-server
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 80
  selector:
    name: elastickube-server
"

SPINNER_STR='|/-\'

retry()
{
    local PID=0
    local COUNTER=0
    local SPINNER_DELAY=0.25
    local TEMP_SPINNER=${SPINNER_STR#?}
    local RETURN_CODE=-1

    SPINNER_STR=${TEMP_SPINNER}${SPINNER_STR%"$TEMP_SPINNER"}

    printf "[ %c ] " "${SPINNER_STR}"
    until [[ ${COUNTER} -ge $[${TIMEOUT} * 4] ]] || [[ ${RETURN_CODE} -eq 0 ]]
    do
        if [[ ${RETURN_CODE} -ne 0 ]]
        then
             eval "$@ 2>>elastickube.log >>elastickube.log &"
             PID=$!
        fi

        while ps a | awk '{print $1}' | grep ${PID} 2>&1 > /dev/null
        do
            TEMP_SPINNER=${SPINNER_STR#?}
            SPINNER_STR=${TEMP_SPINNER}${SPINNER_STR%"$TEMP_SPINNER"}
            printf "\b\b\b\b\b\b[ %c ] " "${SPINNER_STR}"

            sleep ${SPINNER_DELAY}
            COUNTER=$[${COUNTER} + 1]
        done

        wait ${PID}
        RETURN_CODE=$?
    done
    printf "\b\b\b\b\b\b    \b\b\b\b"

    return ${RETURN_CODE}
}

check_tool()
{
    printf "%-${PROGRESS_WIDTH}s" "Checking ${1} is available"
    if which ${1} > /dev/null 2>&1
    then
        echo [ ✓ ]
    else
        echo [ NOT FOUND ] && exit 1
    fi
}

deploy_rc()
{
    printf "%-${PROGRESS_WIDTH}s" "Setting up ${1}"
    if ! kubectl --namespace=kube-system get rc ${1} 2>>elastickube.log >>elastickube.log
    then
        echo "${2}" | kubectl create --validate=false -f - 2>>elastickube.log >>elastickube.log
    fi

    if retry "kubectl --namespace=kube-system describe rc ${1} 2>>elastickube.log | grep '1 Running / 0 Waiting / 0 Succeeded / 0 Failed'"
    then
        echo [ ✓ ]
    else
        echo [ FAILED ] && exit 1
    fi
}

deploy_svc()
{
    printf "%-${PROGRESS_WIDTH}s" "Setting up ${1} svc"
    if ! kubectl --namespace=kube-system get svc ${1} 2>>elastickube.log >>elastickube.log
    then
        if echo "${2}" | kubectl create --validate=false -f - 2>>elastickube.log >>elastickube.log
        then
            echo [ ✓ ]
        else
            echo [ FAILED ] && exit 1
        fi
    else
        echo [ ✓ ]
    fi
}

# Check gcloud and kubectl is installed
check_tool kubectl

# Check the cluster is configured
printf "%-${PROGRESS_WIDTH}s" "Verifying Kubernetes cluster"
if kubectl cluster-info 2>>elastickube.log >>elastickube.log
then
    echo [ ✓ ]
else
    echo [ NOT RUNNING ]
fi

deploy_svc elastickube-server "${ELASTICKUBE_SERVER_SVC}"
deploy_svc elastickube-mongo  "${ELASTICKUBE_MONGO_SVC}"
deploy_rc  elastickube-mongo  "${ELASTICKUBE_MONGO_RC}"
deploy_rc  elastickube-server "${ELASTICKUBE_SERVER_RC}"

# Detect whether this is a GKE LoadBalancer
if kubectl get pods --namespace=kube-system -l name=glbc 2>>elastickube.log | grep "Running"  >>elastickube.log
then
    LOADBALANCER_IP_PROPERTY='LoadBalancer Ingress:'
else
    LOADBALANCER_IP_PROPERTY='IP:'
cat << \
______________________________RESULT______________________________
$(tput sgr0)$(tput bold)WARNING:$(tput sgr0) LoadBalancer Ingress not detected, please ensure the address is accessible from outside the cluster. Check http://kubernetes.io/docs/user-guide/ingress/ for more information.
______________________________RESULT______________________________
fi

printf "%-${PROGRESS_WIDTH}s" "Waiting for LB to be ready"
if retry "kubectl --namespace=kube-system describe svc elastickube-server | grep -e '${LOADBALANCER_IP_PROPERTY}'"
then
    echo [ ✓ ]
else
    echo [ FAILED ] && exit 1
fi

cat << \
______________________________RESULT______________________________

ElasticKube has been deployed!
Please complete the installation here: $(tput sgr0)$(tput bold)http://$(kubectl --namespace=kube-system describe svc elastickube-server | grep -e "${LOADBALANCER_IP_PROPERTY}" | cut -d ":" -f 2 | xargs)$(tput sgr0)
______________________________RESULT______________________________
