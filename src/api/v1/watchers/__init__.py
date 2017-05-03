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


def filter_namespaces(data, user, _message, _settings):
    if user["role"] != "administrator":
        if isinstance(data, list):
            for item in data:
                if "members" not in item or user["username"] not in item["members"]:
                    data.remove(item)

            return data
        else:
            if "members" not in data or user["username"] not in data["members"]:
                return

    return data


def filter_metrics(data, _user, message, _settings):
    if "body" in message and "name" in message["body"]:
        if ("involvedObject" in data and
                "name" in data["involvedObject"] and
                data["involvedObject"]["name"] == message["body"]["name"]):
            return data
        else:
            return None
    else:
        return data

    return data


def criteria_notifications(user, _message, _settings):
    criteria = {
        'user': user['username'],
        'unread': True
    }

    return criteria
