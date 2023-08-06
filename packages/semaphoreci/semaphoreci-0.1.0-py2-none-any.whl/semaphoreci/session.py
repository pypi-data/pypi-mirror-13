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
"""Module containing the implementation details of SemaphoreCI Sessions."""

import requests

from . import __version__ as semaphoreci_version
from . import exceptions
from . import utils

__all__ = ('SemaphoreCI',)


class SemaphoreCI(object):
    """Wrapper for the Semaphore CI API.

    See also the API documentation `here`_.

    .. _here: https://semaphoreci.com/docs/api.html
    """

    def __init__(self, auth_token, formatter=None):
        """Initialize a SemaphoreCI instance.

        :param str auth_token:
            Semaphore CI Authentication Token
        :param callable formatter:
            Function or object to call to format return values from this
            class. This defaults to calling the ``Response.json()`` method on
            each response. This is only passed the response instance.
        """
        if auth_token is None:
            raise ValueError(
                "All methods require an authentication token. See "
                "https://semaphoreci.com/docs/api_authentication.html "
                "for how to retrieve an authentication token from Semaphore"
                " CI."
            )

        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'python-semaphoreci/{}'.format(
            semaphoreci_version
        )
        self.session.params = {}
        self.auth_token = auth_token
        self.formatter = formatter or _default_formatter

    def _get_formatted(self, url, params=None):
        response = self.session.get(url, params=params)
        exceptions.raise_for_status(response)
        return self.formatter(response)

    @property
    def auth_token(self):
        """The authentication token for your SemaphoreCI account."""
        return self.session.params['auth_token']

    @auth_token.setter
    def auth_token(self, token):
        """The authentication token for your SemaphoreCI account."""
        self.session.params['auth_token'] = token

    def branch_history(self, project, branch, page_number=1):
        """Get the history of the branch.

        See also
        https://semaphoreci.com/docs/branches-and-builds-api.html#branch_status

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :param branch:
            either the branch's ``id`` or a ``branch`` from listing your
            project's branches
        :returns:
            dictionary with the builds listed inside
        :rtype:
            dict
        """
        project_id = utils.get_project_id(project)
        branch_id = utils.get_branch_id(branch)
        url = 'https://semaphoreci.com/api/v1/projects/{hash_id}/{id}'
        params = {'page': str(page_number)}
        return self._get_formatted(url.format(hash_id=project_id,
                                              id=branch_id),
                                   params=params)

    def branch_status(self, project, branch):
        """Get the status for a branch on a particular project.

        See also
        https://semaphoreci.com/docs/branches-and-builds-api.html#branch_status

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :param branch:
            either the branch's ``id`` or a ``branch`` from listing your
            project's branches
        :returns:
            dictionary with information about a branch's status
        :rtype:
            dict
        """
        project_id = utils.get_project_id(project)
        branch_id = utils.get_branch_id(branch)
        url = 'https://semaphoreci.com/api/v1/projects/{hash_id}/{id}/status'
        return self._get_formatted(url.format(hash_id=project_id,
                                              id=branch_id))

    def branches(self, project):
        """List branches for for a project.

        See also
        https://semaphoreci.com/docs/branches-and-builds-api.html#project_branches

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :returns:
            list of dictionaries representing branches
        :rtype:
            list
        """
        project_id = utils.get_project_id(project)
        url = 'https://semaphoreci.com/api/v1/projects/{hash_id}/branches'
        return self._get_formatted(url.format(hash_id=project_id))

    def build_information(self, project, branch, build):
        """Retrieve the build information for a project, branch, and build.

        See also
        https://semaphoreci.com/docs/branches-and-builds-api.html#build_information

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :param branch:
            either the branch's ``id`` or a ``branch`` from listing your
            project's branches
        :param build:
            either the build's ``build_number``, ``number``, or a ``build``
            returned from a method that returns build data
        :returns:
            dictionary containing the build's information
        :rtype:
            dict
        """
        project_id = utils.get_project_id(project)
        branch_id = utils.get_branch_id(branch)
        build_number = utils.get_build_number(build)
        url = ('https://semaphoreci.com/api/v1/projects/{hash_id}/{id}'
               '/builds/{number}')
        return self._get_formatted(url.format(hash_id=project_id,
                                              id=branch_id,
                                              number=build_number))

    def build_log(self, project, branch, build):
        """Retrieve the build log for a project, branch, and build.

        See also
        https://semaphoreci.com/docs/branches-and-builds-api.html#build_log

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :param branch:
            either the branch's ``id`` or a ``branch`` from listing your
            project's branches
        :param build:
            either the build's ``build_number``, ``number``, or a ``build``
            returned from a method that returns build data
        :returns:
            dictionary containing the build's log
        :rtype:
            dict
        """
        project_id = utils.get_project_id(project)
        branch_id = utils.get_branch_id(branch)
        build_number = utils.get_build_number(build)
        url = ('https://semaphoreci.com/api/v1/projects/{hash_id}/{id}'
               '/builds/{number}/log')
        return self._get_formatted(url.format(hash_id=project_id,
                                              id=branch_id,
                                              number=build_number))

    def launch_build(self, project, branch, commit_sha):
        """Launch a build for a project's branch at a specific SHA.

        See also
        https://semaphoreci.com/docs/branches-and-builds-api.html#launch_build

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :param branch:
            either the branch's ``id`` or a ``branch`` from listing your
            project's branches
        :param str commit_sha:
            the SHA of the commit to build
        :returns:
            dictionary similar to the return value of
            :method:`~SemaphoreCI.build_information`
        :rtype:
            dict
        """
        project_id = utils.get_project_id(project)
        branch_id = utils.get_branch_id(branch)
        params = {'commit_sha': commit_sha}
        url = 'https://semaphoreci.com/api/v1/projects/{hash_id}/{id}/build'
        response = self.session.post(url.format(hash_id=project_id,
                                                id=branch_id),
                                     params=params)
        exceptions.raise_for_status(response)
        return self.formatter(response)

    def projects(self):
        """List the authenticated user's projects and their current status.

        See also
        https://semaphoreci.com/docs/projects-api.html

        :returns:
            list of dictionaries representing projects and their current
            status
        :rtype:
            list
        """
        return self._get_formatted('https://semaphoreci.com/api/v1/projects')

    def rebuild_last_revision(self, project, branch):
        """Rebuild the last revision of a project's branch.

        See also
        https://semaphoreci.com/docs/branches-and-builds-api.html#rebuild

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :param branch:
            either the branch's ``id`` or a ``branch`` from listing your
            project's branches
        :returns:
            dictionary similar to the return value of
            :method:`~SemaphoreCI.build_information`
        :rtype:
            dict
        """
        project_id = utils.get_project_id(project)
        branch_id = utils.get_branch_id(branch)
        url = 'https://semaphoreci.com/api/v1/projects/{hash_id}/{id}/build'
        response = self.session.post(url.format(hash_id=project_id,
                                                id=branch_id))
        exceptions.raise_for_status(response)
        return self.formatter(response)

    def servers(self, project):
        """List the servers associated with the specified project.

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :returns:
            list of the project's servers
        :rtype:
            list
        """
        project_id = utils.get_project_id(project)
        url = 'https://semaphoreci.com/api/v1/projects/{hash_id}/servers'
        return self._get_formatted(url.format(hash_id=project_id))

    def stop_build(self, project, branch, build):
        """Stop the specified build on that project and branch.

        :param project:
            either the project's ``hash_id`` or a ``project`` from
            listing your projects
        :param branch:
            either the branch's ``id`` or a ``branch`` from listing your
            project's branches
        :param build:
            either the build's ``build_number``, ``number``, or a ``build``
            returned from a method that returns build data
        :returns:
            dictionary similar to the return value of
            :method:`~SemaphoreCI.build_information`
        :rtype:
            dict
        """
        project_id = utils.get_project_id(project)
        branch_id = utils.get_branch_id(branch)
        build_number = utils.get_build_number(build)
        url = ('https://semaphoreci.com/api/v1/projects/{hash_id}/{id}/builds'
               '/{number}/stop')
        response = self.session.post(url.format(hash_id=project_id,
                                                id=branch_id,
                                                number=build_number))
        exceptions.raise_for_status(response)
        return self.formatter(response)


def _default_formatter(response):
    return response.json()
