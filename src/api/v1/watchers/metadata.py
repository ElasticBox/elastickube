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

import pymongo

from api.v1.watchers import criteria_notifications, filter_metrics, filter_namespaces, filter_notifications


class WatcherMetadata(object):

    def __init__(self, action):
        self.action = action

    def get(self, settings):
        return {
            "users": {
                "collection": "Users",
                "projection": {"password": 0},
                "criteria": {},
                "sort": None,
                "limit": 0,
                "filter_data": None,
                "manipulate": False
            },
            "namespaces": {
                "collection": "Namespaces",
                "projection": None,
                "criteria": {},
                "sort": None,
                "limit": 0,
                "filter_data": filter_namespaces,
                "manipulate": False
            },
            "settings": {
                "collection": "Settings",
                "projection": None,
                "criteria": {},
                "sort": None,
                "limit": 0,
                "filter_data": None,
                "manipulate": False
            },
            "charts": {
                "collection": "Charts",
                "projection": None,
                "criteria": {},
                "sort": None,
                "limit": 0,
                "filter_data": None,
                "manipulate": True
            },
            "metrics": {
                "collection": "Metrics",
                "projection": None,
                "criteria": {},
                "limit": 500,
                "sort": [("timestamp", pymongo.DESCENDING)],
                "filter_data": filter_metrics,
                "manipulate": False
            },
            "notifications": {
                "collection": "Notifications",
                "projection": None,
                "criteria": criteria_notifications,
                "sort": [("metadata.creationTimestamp", pymongo.DESCENDING)],
                "limit": 10,
                "filter_data": filter_notifications,
                "manipulate": True
            },
            "instances": {
                "required_params": [],
                "init": {
                    "resources": {
                        "pods": {
                            "resource": "pods",
                            "type": "PodList",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s"
                            }
                        },
                        "replicationcontrollers": {
                            "resource": "replicationcontrollers",
                            "type": "ReplicationControllerList",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s"
                            }
                        },
                        "services": {
                            "resource": "services",
                            "type": "ServiceList",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s"
                            }
                        }
                    }
                },
                "watch": {
                    "resources": {
                        "pods": {
                            "resource": "pods",
                            "type": "PodList",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "resourceVersion": "%(resourceVersionPodList)s"
                            }
                        },
                        "replicationcontrollers": {
                            "resource": "replicationcontrollers",
                            "type": "ReplicationControllerList",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "resourceVersion": "%(resourceVersionReplicationControllerList)s"
                            }
                        },
                        "services": {
                            "resource": "services",
                            "type": "ServiceList",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "resourceVersion": "%(resourceVersionServiceList)s"
                            }
                        }
                    }
                }
            },
            "pod": {
                "params": ["namespace", "kind", "name"],
                "required_params": ["namespace", "kind", "name"],
                "init": {
                    "resources": {
                        "pods": {
                            "resource": "pods",
                            "type": "Pod",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s"
                            }
                        },
                        "metrics": {
                            "resource": "pods",
                            "type": "MetricList",
                            "method": "METRICS",
                            "parameters": {
                                "heapster_client": settings["heapster"],
                                "namespace": "%(namespace)s",
                                "name": "%(name)s"
                            }
                        },
                        "events": {
                            "resource": "events",
                            "type": "EventList",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "fieldSelector": ("involvedObject.name=%(name)s,"
                                                  "involvedObject.namespace=%(namespace)s,"
                                                  "involvedObject.uid=%(uid)s")
                            }
                        }
                    }
                },
                "watch": {
                    "resources": {
                        "pods": {
                            "type": "Pod",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s",
                                "resourceVersion": "%(resourceVersionPod)s"
                            }
                        },
                        "events": {
                            "type": "EventList",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "resourceVersion": "%(resourceVersionEventList)s",
                                "fieldSelector": ("involvedObject.name=%(name)s,"
                                                  "involvedObject.namespace=%(namespace)s,"
                                                  "involvedObject.uid=%(uid)s")
                            }
                        }
                    }
                }
            },
            "replicationcontroller": {
                "params": ["namespace", "kind", "name"],
                "required_params": ["namespace", "kind", "name"],
                "init": {
                    "resources": {
                        "replicationcontrollers": {
                            "resource": "replicationcontrollers",
                            "type": "ReplicationController",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s"
                            }
                        },
                        "events": {
                            "resource": "events",
                            "type": "EventList",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "fieldSelector": ("involvedObject.name=%(name)s,"
                                                  "involvedObject.kind=%(kind)s,"
                                                  "involvedObject.namespace=%(namespace)s,"
                                                  "involvedObject.uid=%(uid)s")
                            }
                        }
                    }
                },
                "watch": {
                    "resources": {
                        "replicationcontrollers": {
                            "resource": "replicationcontrollers",
                            "type": "ReplicationController",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s",
                                "resourceVersion": "%(resourceVersionReplicationController)s"
                            }
                        },
                        "events": {
                            "resource": "events",
                            "type": "EventList",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "resourceVersion": "%(resourceVersionEventList)s",
                                "fieldSelector": ("involvedObject.name=%(name)s,"
                                                  "involvedObject.kind=%(kind)s,"
                                                  "involvedObject.namespace=%(namespace)s,"
                                                  "involvedObject.uid=%(uid)s")
                            }
                        }
                    }
                }
            },
            "service": {
                "params": ["namespace", "kind", "name"],
                "required_params": ["namespace", "kind", "name"],
                "init": {
                    "resources": {
                        "services": {
                            "resource": "services",
                            "type": "Service",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s"
                            }
                        },
                        "endpoints": {
                            "resource": "endpoints",
                            "type": "Endpoints",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s"
                            }
                        },
                        "events": {
                            "resource": "events",
                            "type": "EventList",
                            "method": "GET",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "fieldSelector": ("involvedObject.name=%(name)s,"
                                                  "involvedObject.kind=%(kind)s,"
                                                  "involvedObject.namespace=%(namespace)s,"
                                                  "involvedObject.uid=%(uid)s")
                            }
                        }
                    }
                },
                "watch": {
                    "resources": {
                        "services": {
                            "resource": "services",
                            "type": "Service",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s",
                                "resourceVersion": "%(resourceVersionService)s"
                            }
                        },
                        "endpoints": {
                            "resource": "endpoints",
                            "type": "Endpoints",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "name": "%(name)s",
                                "resourceVersion": "%(resourceVersionEndpoints)s"
                            }
                        },
                        "events": {
                            "resource": "events",
                            "type": "EventList",
                            "method": "WATCH",
                            "parameters": {
                                "namespace": "%(namespace)s",
                                "resourceVersion": "%(resourceVersionEventList)s",
                                "fieldSelector": ("involvedObject.name=%(name)s,"
                                                  "involvedObject.kind=%(kind)s,"
                                                  "involvedObject.namespace=%(namespace)s,"
                                                  "involvedObject.uid=%(uid)s")
                            }
                        }
                    }
                }
            }
        }.get(self.action, None)
