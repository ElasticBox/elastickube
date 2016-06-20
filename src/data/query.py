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

import time

from bson.objectid import ObjectId
from pymongo.errors import PyMongoError
from tornado.gen import coroutine, Return


class ObjectNotFoundError(PyMongoError):
    """Raised when object is not found into the collection.
    """


class Query(object):

    def __init__(self, database, collection, manipulate=False):
        self.database = database
        self.collection = collection
        self.manipulate = manipulate

        self.default_criteria = {"$and": [{"metadata.deletionTimestamp": None}]}

    def _generate_query(self, criteria):
        query = self.default_criteria
        if criteria:
            if len(criteria) > 1:
                for key, value in criteria.iteritems():
                    query['$and'].append({key: value})
            else:
                query['$and'].append(criteria)

        return query

    @coroutine
    def find_one(self, criteria=None, projection=None):
        document = yield self.database[self.collection].find_one(
            self._generate_query(criteria),
            projection,
            manipulate=self.manipulate)
        raise Return(document)

    @coroutine
    def find(self, criteria=None, projection=None, sort=None, limit=0):
        documents = []

        cursor = self.database[self.collection].find(
            self._generate_query(criteria),
            projection,
            sort=sort,
            limit=limit,
            manipulate=self.manipulate)
        while (yield cursor.fetch_next):
            documents.append(cursor.next_object())

        raise Return(documents)

    @coroutine
    def insert(self, document):
        if "metadata" in document:
            document["metadata"]["resourceVersion"] = time.time()
            document["metadata"]["creationTimestamp"] = time.time()
            document["metadata"]["deletionTimestamp"] = None
        else:
            document["metadata"] = dict(
                resourceVersion=time.time(),
                creationTimestamp=time.time(),
                deletionTimestamp=None
            )

        if '_id' not in document and not self.manipulate:
            document['_id'] = ObjectId()
        document_id = yield self.database[self.collection].insert(document, manipulate=self.manipulate)
        inserted_document = yield self.database[self.collection].find_one(
            {"_id": document_id},
            manipulate=self.manipulate)
        raise Return(inserted_document)

    @coroutine
    def update(self, document):
        document["metadata"]["resourceVersion"] = time.time()
        response = yield self.database[self.collection].update(
            {"_id": document["_id"]},
            document,
            upsert=True,
            manipulate=self.manipulate)
        if response['n'] == 0:
            raise ObjectNotFoundError()

        updated_document = yield self.database[self.collection].find_one(
            {"_id": document["_id"]},
            manipulate=self.manipulate)
        raise Return(updated_document)

    @coroutine
    def update_fields(self, criteria, fields):
        update = {"$set": fields}
        update["$set"]["metadata.resourceVersion"] = time.time()

        response = yield self.database[self.collection].update(criteria, update, manipulate=self.manipulate)
        raise Return(response)

    @coroutine
    def remove(self, document):
        response = yield self.database[self.collection].remove({"_id": document["_id"]})
        raise Return(response)

    @coroutine
    def aggregate(self, pipeline):
        aggregations = []

        cursor = self.database[self.collection].aggregate(pipeline)
        while (yield cursor.fetch_next):
            aggregations.append(cursor.next_object())

        raise Return(aggregations)
