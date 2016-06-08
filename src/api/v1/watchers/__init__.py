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

import logging

from tornado.gen import coroutine, Return

from data.query import Query


@coroutine
def filter_namespaces(data, user, _message, _settings):
    if user["role"] != "administrator":
        if isinstance(data, list):
            for item in data:
                if "members" not in item or user["username"] not in item["members"]:
                    data.remove(item)

            raise Return(data)
        else:
            if "members" not in data or user["username"] not in data["members"]:
                raise Return()

    raise Return(data)


@coroutine
def filter_metrics(data, _user, _message, _settings):
    raise Return(data)


@coroutine
def filter_notifications(data, user, message, settings):
    criteria = yield criteria_notifications(user, message, settings)
    logging.warn('User %s' % user)
    if user.get("notifications_viewed_at", None):
        criteria = {'$and': [
            criteria,
            {"metadata.creationTimestamp": {"$gt": user["notifications_viewed_at"]}}
        ]}

    unread_namespaces = yield Query(settings["database"], "Notifications").aggregate([
        {'$match': criteria},
        {'$group': {'_id': '$namespace', 'unread': {'$sum': 1}}}
    ])

    total_unread = 0
    for namespace in unread_namespaces:
        namespace['name'] = namespace.pop('_id')
        total_unread += namespace['unread']

    info = {'total_unread': total_unread, 'unread_namespaces': unread_namespaces}
    if isinstance(data, list):
        info["latest"] = data
    else:
        info["notification"] = data

    raise Return(info)
    

@coroutine
def criteria_notifications(user, message, settings):
    criteria = {}

    if user["role"] != "administrator":
        namespaces = yield Query(settings["database"], "Namespaces").find(
            criteria={"members": user["username"]},
            projection=["name"])
        criteria["namespace"] = {'$in': [n["name"] for n in namespaces]}

    raise Return(criteria)
