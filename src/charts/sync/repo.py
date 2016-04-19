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

import binascii
import glob
import logging
import os

from git.repo import Repo
from git.exc import InvalidGitRepositoryError
from tornado.gen import coroutine, Return, sleep
from yaml import load, load_all


from data import DEFAULT_GITREPO
from data.query import Query
from data.watch import add_callback

REPO_DIRECTORY = '/var/elastickube/charts'


class GitSync(object):

    def __init__(self, database):
        logging.info("Initializing GitSync.")

        self.database = database
        self.charts = dict()
        self.url = DEFAULT_GITREPO

        try:
            self.repo = Repo(REPO_DIRECTORY)
        except InvalidGitRepositoryError:
            logging.info("Cloning repository in %s", REPO_DIRECTORY)
            self.repo = Repo.clone_from(self.url, REPO_DIRECTORY)

    @coroutine
    def update_repo(self, document):
        if document['o']["charts"]["repo_url"] != self.url:
            logging.info("Repo url updated to '%s'.", document['o']["charts"]["repo_url"])
            self.url = document['o']["charts"]["repo_url"]

    @coroutine
    def sync_loop(self):
        logging.info("Initializing sync loop.")
        yield add_callback("Settings", self.update_repo)

        synced_head = None

        settings = yield Query(self.database, "Settings").find_one() or dict()
        if settings["charts"]:
            self.url = settings["charts"]["repo_url"]

        while True:
            try:
                if self.url != self.repo.remotes.origin.url:
                    logging.info("Changing reference from '%s' to '%s'.", self.repo.remotes.origin.url, self.url)
                    self.repo.delete_remote('origin')
                    self.repo.create_remote('origin', url=self.url)
                    synced_head = None

                self.repo.git.fetch('--all')
                self.repo.git.reset('--hard', 'origin/master')

                if synced_head != self.repo.head.ref.commit:
                    yield self.sync()
                    synced_head = self.repo.head.ref.commit

            except:
                logging.exception("Failed to pull repository.")

            yield sleep(5)

    @coroutine
    def sync(self):
        logging.info("Syncing '%s'.", REPO_DIRECTORY)

        charts = yield Query(self.database, "Charts").find()
        for chart in charts:
            path = chart["path"]
            self.charts[path] = chart

        discovered_charts = dict()
        for subdir, _, files in os.walk(REPO_DIRECTORY):
            for chart_file in files:
                if chart_file == "Chart.yaml":
                    try:
                        discovered_charts[subdir] = yield self.import_chart(subdir)
                    except Exception:
                        logging.exception("Failed to import chart at '%s'", subdir)

        for path, existing in self.charts.iteritems():
            discovered = discovered_charts.get(path, None)

            if discovered is None:
                logging.debug("Deleting chart %(name)s", existing)
                yield Query(self.database, 'Charts').remove(existing)
            else:
                discovered["_id"] = existing["_id"]
                discovered["metadata"] = existing["metadata"]

                if discovered["commit"] != existing["commit"]:
                    logging.debug("Updating existing chart %(name)s", discovered)

                    try:
                        yield Query(self.database, "Charts").update(discovered)
                    except Exception as error:
                        logging.exception("Failed to update chart %(name)s", discovered)

        for path, discovered in discovered_charts.iteritems():
            if discovered and "_id" not in discovered:
                logging.debug("Inserting new chart %(name)s", discovered)
                try:
                    yield Query(self.database, "Charts").insert(discovered)
                except:
                    logging.exception("Failed to insert chart %(name)s", discovered)

        self.charts = discovered_charts

    @coroutine
    def import_chart(self, directory):
        chart_path = os.path.join(directory, "Chart.yaml")

        with open(chart_path, "r") as stream:
            chart = load(stream)
            chart["path"] = directory

            commit = self.repo.iter_commits(paths=chart_path).next()
            chart["commit"] = binascii.hexlify(commit.binsha)
            chart["committed_date"] = commit.committed_date
            chart["resources"] = []

            manifests = yield self.import_manifests(directory)
            for _, manifest in manifests.iteritems():
                if commit.committed_date < manifest["commit"].committed_date:
                    chart["commit"] = binascii.hexlify(manifest["commit"].binsha)
                    chart["committed_date"] = manifest["commit"].committed_date

                for resource in manifest["resources"]:
                    chart["resources"].append(resource)

            raise Return(chart)

    @coroutine
    def import_manifests(self, directory):
        manifests = dict()

        manifests_path = os.path.join(directory, "manifests", "*.yaml")
        for manifest in glob.glob(manifests_path):
            with open(manifest, "r") as stream:
                manifests[manifest] = dict(
                    resources=[resource for resource in load_all(stream)],
                    commit=self.repo.iter_commits(paths=manifest).next()
                )

        raise Return(manifests)
