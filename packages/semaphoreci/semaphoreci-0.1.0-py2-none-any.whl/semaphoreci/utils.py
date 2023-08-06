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
"""Module containing utility functions for semaphoreci wrapper library."""


def generic_attribute_retriever(obj, attribute, alternate_attribute=None):
    try:
        value = obj.get(attribute)
        if (value is None and
                attribute not in obj and
                alternate_attribute is not None):
            value = obj.get(alternate_attribute)
        return value
    except AttributeError:
        return obj


def get_branch_id(branch):
    return generic_attribute_retriever(branch, 'id')


def get_build_number(build):
    return generic_attribute_retriever(build, 'build_number', 'number')


def get_project_id(project):
    return generic_attribute_retriever(project, 'hash_id')


def get_session(session):
    return getattr(session, 'semaphoreci', session)
