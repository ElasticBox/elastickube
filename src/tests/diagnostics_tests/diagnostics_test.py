"""
Copyright 2016 ElasticBox All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import, unicode_literals

import copy
import json
import logging
import os
import sys

from concurrent.futures import Future
import mock
import pytest

from diagnostics import diagnostics


logging.basicConfig(level=logging.DEBUG)


# Extra requirements to run the tests
'''
pip install mock
pip install pytest
pip install pytest-tornado
'''


SAMPLE_TOKEN = (
    'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2a'
    'WNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJkZWZ'
    'hdWx0LXRva2VuLTZ5ZHB1Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImRlZmF1bHQiLCJrd'
    'WJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIyZDZhOGFkZC1mNzQ3LTExZTUtYjQyZC0wODAwMjdmZjN'
    'hNmUiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06ZGVmYXVsdCJ9.PQVUwcrHlZbI_I6-LQgqukMrY1-8-ZkEZLpq'
    'VqhN7tZVTKTcxTyuG4BP8vnCa_BOzX6atvmx5XRw7bgcs4K34Tk-r1S8G4HsD6_z0U95wz-nS6sTm0vOXkcZGoGiLRAmwV4-8oLEzTlQWN35zs'
    'pX3YeUsuUEg3WSOLRUI7vDV911dJgAISP8DJ9t9ZwtCrtT9afzb4Kxqk-E-7QqOkqIxPGDwQQodLTiW8LzMDHd-wO5x0C_LFa2lXg8KgwY_xeb'
    '1wApMxgU-rl3RrIRac48CYQnGG-PgDwPdPltRDoex-j2mKuMm682fkmtERjYCtq2mmnHsG5Zhqz4TLXKHc4qkQ')


SAMPLE_REPLICATION_CONTROLLER = {
    "kind": "ReplicationController",
    "apiVersion": "v1",
    "metadata": {
        "name": "elastickube-server",
        "namespace": "kube-system",
        "selfLink": "/api/v1/namespaces/kube-system/replicationcontrollers/elastickube-server",
        "uid": "8a7ac7cd-fa5a-11e5-9085-080027ff3a6e",
        "resourceVersion": "8319",
        "generation": 1,
        "creationTimestamp": "2016-04-04T11:44:08Z",
        "labels": {
            "name": "elastickube-server"
        }
    },
    "spec": {
        "replicas": 1,
        "selector": {
            "name": "elastickube-server"
        },
        "template": {
            "metadata": {
                "creationTimestamp": None,
                "labels": {
                    "name": "elastickube-server"
                }
            },
            "spec": {
                "volumes": [
                    {
                        "name": "elastickube-code",
                        "hostPath": {
                            "path": "/opt/elastickube/src"
                        }
                    },
                    {
                        "name": "elastickube-charts",
                        "hostPath": {
                            "path": "/var/elastickube/charts"
                        }
                    },
                    {
                        "name": "elastickube-run",
                        "hostPath": {
                            "path": "/var/run/elastickube"
                        }
                    },
                    {
                        "name": "elasticbox-home-user",
                        "hostPath": {
                            "path": "/home/elasticbox"
                        }
                    }
                ],
                "containers": [
                    {
                        "name": "elastickube-api",
                        "image": "elasticbox/elastickube-api:latest",
                        "resources": {
                            "limits": {
                                "cpu": "100m",
                                "memory": "128Mi"
                            }
                        },
                        "volumeMounts": [
                            {
                                "name": "elastickube-code",
                                "mountPath": "/opt/elastickube"
                            },
                            {
                                "name": "elastickube-run",
                                "mountPath": "/var/run"
                            },
                            {
                                "name": "elasticbox-home-user",
                                "mountPath": "/home/elasticbox"
                            }
                        ],
                        "terminationMessagePath": "/dev/termination-log",
                        "imagePullPolicy": "Never"
                    },
                    {
                        "name": "elastickube-charts",
                        "image": "elasticbox/elastickube-charts:latest",
                        "resources": {
                            "limits": {
                                "cpu": "50m",
                                "memory": "64Mi"
                            }
                        },
                        "volumeMounts": [
                            {
                                "name": "elastickube-code",
                                "mountPath": "/opt/elastickube"
                            },
                            {
                                "name": "elastickube-charts",
                                "mountPath": "/var/elastickube/charts"
                            }
                        ],
                        "terminationMessagePath": "/dev/termination-log",
                        "imagePullPolicy": "Never"
                    },
                    {
                        "name": "elastickube-nginx",
                        "image": "elasticbox/elastickube-nginx:latest",
                        "ports": [
                            {
                                "name": "http",
                                "hostPort": 80,
                                "containerPort": 80,
                                "protocol": "TCP"
                            }
                        ],
                        "resources": {
                            "limits": {
                                "cpu": "10m",
                                "memory": "32Mi"
                            }
                        },
                        "volumeMounts": [
                            {
                                "name": "elastickube-code",
                                "mountPath": "/opt/elastickube"
                            },
                            {
                                "name": "elastickube-run",
                                "mountPath": "/var/run"
                            }
                        ],
                        "terminationMessagePath": "/dev/termination-log",
                        "imagePullPolicy": "Never"
                    }
                ],
                "restartPolicy": "Always",
                "terminationGracePeriodSeconds": 30,
                "dnsPolicy": "ClusterFirst",
                "securityContext": {}
            }
        }
    },
    "status": {
        "replicas": 1,
        "fullyLabeledReplicas": 1,
        "observedGeneration": 1
    }
}


@pytest.fixture
def token_path(tmpdir):
    token_file = tmpdir.join('token_content')
    token_file.write(SAMPLE_TOKEN)

    return str(token_file)


@pytest.fixture
def env(token_path):
    return {'KUBERNETES_SERVICE_PORT': '8080',
            'KUBERNETES_SERVICE_HOST': '10.107.56.115',
            'KUBE_API_TOKEN_PATH': token_path,
            'DNS_TEST_HOSTNAME': 'google.com',  # Use a public DNS not kubernetes.default for testing outside kubernetes
            'HEAPSTER_SERVICE_HOST': '10.0.127.162',
            'HEAPSTER_SERVICE_PORT': '80',
            }


@pytest.fixture
def settings():
    return {'kubernetes_url': 'http://10.107.56.115:8080', 'token': SAMPLE_TOKEN,
            'check_connectivity_url': 'http://google.com', 'dns_test_hostname': 'google.com',
            'HEAPSTER_SERVICE_HOST': '10.0.127.162', 'HEAPSTER_SERVICE_PORT': '80',
            'KUBERNETES_SERVICE_HOST': '10.107.56.115', 'KUBERNETES_SERVICE_PORT': '8080',
            }


@pytest.fixture
def replica_names():
    return [
        ('kube-system', 'elastickube-server'),
        ('kube-system', 'elastickube-mongo'),
    ]


@pytest.fixture
def status(replica_names):
    return diagnostics.SystemStatus(replica_names)


@pytest.fixture
def status_ok(status):
    status.internet = diagnostics.status_ok()
    status.kubernetes = diagnostics.status_ok()
    status.dns = diagnostics.status_ok()
    status.heapster = diagnostics.status_ok()
    for name in status.rcs:
        status.rcs[name] = diagnostics.status_ok()

    return status


@pytest.fixture
def app(status):
    statics_path = os.path.join(os.path.dirname(__file__), 'assets')
    return diagnostics.create_application(status, statics_path, debug=False)


@pytest.fixture
def rc_document():
    return copy.deepcopy(SAMPLE_REPLICATION_CONTROLLER)


def test_settings_from_env_http(env):
    settings = {}
    env['KUBERNETES_SERVICE_PORT'] = '80'
    diagnostics.settings_from_env(settings, env)
    assert settings['kubernetes_url'] == 'http://10.107.56.115:80'


def test_settings_from_env_custom_port(env):
    settings = {}
    env['KUBERNETES_SERVICE_PORT'] = '8080'
    diagnostics.settings_from_env(settings, env)
    assert settings['kubernetes_url'] == 'http://10.107.56.115:8080'


def test_settings_from_env_https(env):
    settings = {}
    env['KUBERNETES_SERVICE_PORT'] = '443'
    diagnostics.settings_from_env(settings, env)
    assert settings['kubernetes_url'] == 'https://10.107.56.115:443'


def test_settings_from_env_missing_kube_api_key(env):
    settings = {}
    del env['KUBE_API_TOKEN_PATH']
    diagnostics.settings_from_env(settings, env)
    assert settings['token'] is None


def test_default_settings_connectivity_url(env):
    settings = {}
    env['CHECK_CONNECTIVITY_URL'] = 'TEST_URL.COM'
    diagnostics.settings_from_env(settings, env)
    assert settings['check_connectivity_url'] == 'TEST_URL.COM'


def test_default_settings_dns(env):
    settings = {}
    env['DNS_TEST_HOSTNAME'] = 'TEST_URL.COM'
    diagnostics.settings_from_env(settings, env)
    assert settings['dns_test_hostname'] == 'TEST_URL.COM'


def test_default_settings_from_default_env(env, settings):
    base_settings = {}
    diagnostics.settings_from_env(base_settings, env)
    assert base_settings == settings


# System status tests
def test_system_status_initial(status):
    serialized_status = json.dumps(status.to_view())
    assert 'internet' in serialized_status
    assert 'kubernetes' in serialized_status
    assert 'dns' in serialized_status
    for rc in status.rcs:
        assert rc in serialized_status


def test_system_status_custom_replica_name():
    replica_names = (
        ('namespace', 'name'),
    )
    s = diagnostics.SystemStatus(replica_names)
    serialized_status = s.to_view()
    assert 'namespace.name' in serialized_status
    assert 'internet' in serialized_status
    assert 'kubernetes' in serialized_status


@pytest.mark.integration
@pytest.mark.gen_test
def test_check_kubernetes_status(settings):
    status = yield diagnostics._check_kubernetes_status(settings)
    assert status['reason'] == ''
    assert status['status'] is True


@pytest.mark.gen_test
def test_check_kubernetes_status_wrong_answer(settings):
    with mock.patch('diagnostics.diagnostics._get_json') as get_json:
        get_json.side_effect = IOError('Cannot connect')
        status = yield diagnostics._check_kubernetes_status(settings)
        assert status['reason'] == 'Cannot connect'
        assert status['status'] is False


@pytest.mark.gen_test
def test_check_kubernetes_status_wrong_request(settings):
    with mock.patch('diagnostics.diagnostics._get_json') as get_json:
        get_json.return_value = {}
        status = yield diagnostics._check_kubernetes_status(settings)
        assert 'Missing' in status['reason']
        assert status['status'] is False


def test_document_rc_status_ok(rc_document):
    status = diagnostics._document_rc_status(rc_document)
    assert status['reason'] == ''
    assert status['status'] is True


def test_document_rc_status_missing_replicas(rc_document):
    rc_document['status']['replicas'] = 0
    status = diagnostics._document_rc_status(rc_document)
    assert status['reason'] == 'Current pods 0, desired 1'
    assert status['status'] is False


def test_document_rc_status_too_many_replicas(rc_document):
    rc_document['status']['replicas'] = 2
    status = diagnostics._document_rc_status(rc_document)
    assert status['reason'] == 'Current pods 2, desired 1'
    assert status['status'] is False


def test_document_rc_status_wrong_replicaset(rc_document):
    rc_document['spec']['replicas'] = 2
    status = diagnostics._document_rc_status(rc_document)
    assert status['reason'] == 'Current pods 1, desired 2'
    assert status['status'] is False


def test_document_rc_status_wrong_no_replicas(rc_document):
    del rc_document['spec']['replicas']
    status = diagnostics._document_rc_status(rc_document)
    assert 'Wrong replication controller document' in status['reason']
    assert status['status'] is False


@pytest.mark.integration
@pytest.mark.gen_test
def test_check_rcs_ok(settings, replica_names):
    for namespace, name in replica_names:
        status = yield diagnostics._check_replicaset(settings, namespace, name)
        assert status['reason'] == ''
        assert status['status'] is True


@pytest.mark.integration
@pytest.mark.gen_test
def test_check_internet(settings):
    status = yield diagnostics._check_internet(settings)
    assert status['reason'] == ''
    assert status['status'] is True


@pytest.mark.integration
@pytest.mark.gen_test
def test_check_dns(settings):
    status = yield diagnostics._check_dns(settings)
    assert status['reason'] == ''
    assert status['status'] is True


@pytest.mark.gen_test
def test_check_internet_ioerror(settings):
    settings['check_connectivity_url'] = 'test_url'
    with mock.patch('diagnostics.diagnostics.tornado.httpclient.AsyncHTTPClient') as client:
        fut = Future()
        fut.set_exception(IOError('ERROR TEST'))
        client.return_value.fetch.return_value = fut
        status = yield diagnostics._check_internet(settings)
        assert 'ERROR TEST' in status['reason']
        assert 'test_url' in status['reason']
        assert status['status'] is False


@pytest.mark.gen_test
def test_check_internet_wrong_status_code(settings):
    settings['check_connectivity_url'] = 'test_url'
    with mock.patch('diagnostics.diagnostics.tornado.httpclient.AsyncHTTPClient') as client:
        result = mock.MagicMock()
        result.code = 555
        fut = Future()
        fut.set_result(result)
        client.return_value.fetch.return_value = fut
        status = yield diagnostics._check_internet(settings)
        assert '555' in status['reason']
        assert status['status'] is False


@pytest.mark.integration
@pytest.mark.gen_test
def test_check_replicaset_ok(settings):
    status = yield diagnostics._check_replicaset(settings, 'kube-system', 'elastickube-server')
    assert status['reason'] == ''
    assert status['status'] is True


@pytest.mark.gen_test(run_sync=False)
def test_application_html_initializing(http_client, base_url):
    response = yield http_client.fetch(base_url)
    # assert app is None
    assert response.code == 200
    assert 'Diagnostics' in response.body
    assert 'Initializing' in response.body


@pytest.mark.gen_test(run_sync=False)
def test_application_json_initializing(http_client, base_url, status):
    response = yield http_client.fetch(base_url + '/json')
    assert response.code == 200
    data = json.loads(response.body)
    for name, status in data.items():
        assert status['status'] is None  # Initializing


@pytest.mark.gen_test(run_sync=False)
def test_application_json_internet_ok(http_client, base_url, status):
    status.internet = diagnostics.status_ok()
    response = yield http_client.fetch(base_url + '/json')
    assert response.code == 200
    data = json.loads(response.body)
    assert data['internet']['status'] is True


@pytest.mark.gen_test(run_sync=False)
def test_application_json_rcs_ok(http_client, base_url, status_ok):
    response = yield http_client.fetch(base_url + '/json')
    assert response.code == 200
    data = json.loads(response.body)
    for name in data:
        print name
        assert data[name]['reason'] == ''
        assert data[name]['status'] is True


@pytest.mark.gen_test(run_sync=False)
def test_application_json_kubernetes_no_ok(http_client, base_url, status):
    status.kubernetes = diagnostics.status_error('Failed to connect')
    response = yield http_client.fetch(base_url + '/json')
    assert response.code == 200
    data = json.loads(response.body)
    assert data['kubernetes']['status'] is False
    assert data['kubernetes']['reason'] == 'Failed to connect'
    for name in status.rcs:
        assert data[name]['status'] is None
