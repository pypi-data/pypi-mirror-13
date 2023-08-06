# Copyright 2015 Ian Cordasco
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Module containing the implementation details of SemaphoreCI ORM."""
from . import session
from . import utils


__all__ = (
    'SemaphoreCI', 'Project', 'Branch',
)


class SemaphoreCI(object):
    def __init__(self, auth_token):
        self.semaphoreci = session.SemaphoreCI(
            auth_token=auth_token,
            formatter=_identity_formatter,
        )

    def projects(self):
        projects = self.semaphoreci.projects().json()
        for project in projects:
            yield Project(project, self)


class BaseObject(object):
    def __init__(self, data, session, project_hash_id=None):
        self.original_data = data
        self.semaphoreci = utils.get_session(session)
        self.project_hash_id = project_hash_id
        self._update_attributes()

    def _update_attributes(self):
        pass

    def __getattr__(self, attribute):
        if attribute.startswith('original_'):
            attribute = attribute[9:]
        if attribute not in self.original_data:
            raise AttributeError("'{}' has no attribute '{}'".format(
                self.__class__.__name__, attribute
            ))

        return self.original_data.get(attribute)


class Project(BaseObject):
    def _update_attributes(self):
        self.project_hash_id = self.hash_id

    def branches(self):
        branches = self.semaphoreci.branches(self.original_data).json()
        for branch in branches:
            yield Branch(branch, self, self.project_hash_id)


class Branch(BaseObject):
    def history(self):
        hash_id = self.project_hash_id
        branch = self.original_data
        history = self.semaphoreci.branch_history(hash_id, branch).json()
        return BranchHistory(history, self, hash_id)


class BranchHistory(BaseObject):
    pass


def _identity_formatter(response):
    return response
