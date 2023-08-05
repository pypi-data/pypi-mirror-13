# -*- coding: utf-8 -*-

"""
Copyright 2015 Axibase Corporation or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

https://www.axibase.com/atsd/axibase-apache-2.0.pdf

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
"""


from ._meta_models import Entity

_CREATE_ENTITIES = 'createEntities'


class BatchEntitiesCommand(object):
    def __init__(self, action, entities=None, create_entities=None):
        self.empty = False
        self.action = action

        if action == 'delete-all':
            return
        elif entities is not None and len(entities) > 0:
            self.entities = entities
        else:
            self.empty = True

        if create_entities is not None:
            self.createEntities = create_entities

        self._data_entities = [e.serialize() for e in entities]

    def serialize(self):
        data = {'action': self.action}

        if self.action == 'delete-all':
            return data
        else:
            data['entities'] = self._data_entities

        if hasattr(self, _CREATE_ENTITIES):
            data[_CREATE_ENTITIES] = self.createEntities

        return data

    @staticmethod
    def create_delete_command(*entity_names):
        """
        :param entity_names: list of str
        :return: :class:`.BatchEntitiesCommand` instance
        """
        return BatchEntitiesCommand(
            'delete',
            entities=[Entity(name) for name in entity_names]
        )

    @staticmethod
    def create_add_command(*entities, **kwargs):
        """
        :param entities: :class:`.Entity` objects
        :param kwargs: createEntities=bool
        :return: :class:`.BatchEntitiesCommand` instance
        """
        if _CREATE_ENTITIES in kwargs:
            create_entities = kwargs[_CREATE_ENTITIES]
        else:
            create_entities = None
        return BatchEntitiesCommand(
            'add',
            entities=entities,
            create_entities=create_entities
        )

    @staticmethod
    def create_delete_all_command():
        """
        :return: :class:`.BatchEntitiesCommand` instance
        """
        return BatchEntitiesCommand('delete-all')