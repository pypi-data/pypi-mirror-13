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


from .models import Series
from .models import Property
from .models import Alert
from .models import AlertHistory
from .models import Metric
from .models import Entity
from .models import EntityGroup
from .models import BatchEntitiesCommand
from .exceptions import DataParseException
from .exceptions import ServerException

from ._client import Client
from . import _jsonutil

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


try:
    unicode = unicode
except NameError:
    unicode = str


def _check_name(name):
    if not isinstance(name, (str, unicode)):
        raise TypeError('name should be str')
    if len(name) == 0:
        raise ValueError('name is empty')


class _Service(object):
    def __init__(self, conn):
        if not isinstance(conn, Client):
            raise ValueError('conn should be Client instance')
        self.conn = conn


class SeriesService(_Service):
    def retrieve_series(self, *queries):
        """retrieve series for each query

        :param queries: :class:`.SeriesQuery` objects
        :return: list of :class:`.Series` objects
        """
        data = {'queries': queries}
        resp = self.conn.post('series', data)

        return [_jsonutil.deserialize(r, Series) for r in resp['series']]

    def insert_series(self, *series):
        """
        :param series: :class:`.Series` objects
        :return: True if success
        """
        for s in series:
            if len(s.data) == 0:
                raise DataParseException('data', Series,
                                         'inserting empty series')

        self.conn.post('series/insert', series)
        return True


class PropertiesService(_Service):
    def retrieve_properties(self, *queries):
        """retrieve property for each query

        :param queries: :class:`.PropertiesQuery`
        :return: list of :class:`.Property` objects
        """

        data = {'queries': queries}
        resp = self.conn.post('properties', data)

        return _jsonutil.deserialize(resp, Property)

    def insert_properties(self, *properties):
        """
        :param properties: :class:`.Property`
        :return: True if success
        """

        self.conn.post('properties/insert', properties)
        return True

    def batch_update_properties(self, *commands):
        """
        :param commands: :class:`.BatchPropertyCommand`
        :return: True if success
        """
        commands = [c for c in commands if not c.empty]

        if len(commands):
            self.conn.patch('properties', commands)
            return True
        return False


class AlertsService(_Service):
    def retrieve_alerts(self, *queries):
        """retrieve alert for each query

        :param queries: :class:`.AlertsQuery`
        :return: list of :class:`.Alert` objects
        """
        data = {'queries': queries}
        resp = self.conn.post('alerts', data)

        return _jsonutil.deserialize(resp, Alert)

    def retrieve_alert_history(self, *queries):
        """retrieve history for each query

        :param queries: :class:`.AlertHistoryQuery`
        :return: list of :class:`.AlertHistory` objects
        """
        data = {'queries': queries}
        resp = self.conn.post('alerts/history', data)

        return _jsonutil.deserialize(resp, AlertHistory)

    def batch_update_alerts(self, *commands):
        """
        :param commands: :class:`.BatchAlertCommand`
        :return: True is success
        """
        commands = [c for c in commands if not c.empty]

        if len(commands):
            self.conn.patch('alerts', commands)
            return True
        return False


class MetricsService(_Service):
    def retrieve_metrics(self,
                         expression=None,
                         active=None,
                         tags=None,
                         limit=None):
        """
        :param expression: `str`
        :param active: `bool`
        :param tags: `str`
        :param limit: `int`
        :return: :class:`.Metric` objects
        """
        params = {}
        if expression is not None:
            params['expression'] = expression
        if active is not None:
            params['active'] = active
        if tags is not None:
            params['tags'] = tags
        if limit is not None:
            params['limit'] = limit

        resp = self.conn.get('metrics', params)
        return _jsonutil.deserialize(resp, Metric)

    def retrieve_metric(self, name):
        """
        :param name: `str` metric name
        :return: :class:`.Metric`
        """
        _check_name(name)
        try:
            resp = self.conn.get('metrics/' + quote(name, ''))
        except ServerException as e:
            if e.status_code == 404:
                return None
            else:
                raise e

        return _jsonutil.deserialize(resp, Metric)

    def create_or_replace_metric(self, metric):
        """
        :param metric: :class:`.Metric`
        :return: True if success
        """
        self.conn.put('metrics/' + quote(metric.name, ''), metric)
        return True

    def update_metric(self, metric):
        """
        :param metric: :class:`.Metric`
        :return: True if success
        """
        self.conn.patch('metrics/' + quote(metric.name, ''), metric)
        return True

    def delete_metric(self, metric):
        """
        :param metric: :class:`.Metric`
        :return: True if success
        """
        self.conn.delete('metrics/' + quote(metric.name, ''))
        return True


class EntitiesService(_Service):
    def retrieve_entities(self,
                          expression=None,
                          active=None,
                          tags=None,
                          limit=None):
        """
        :param expression: `str`
        :param active: `bool`
        :param tags: `str`
        :param limit: `int`
        :return: `list` of :class:`.Entity` objects
        """
        params = {}
        if expression is not None:
            params['expression'] = expression
        if active is not None:
            params['active'] = active
        if tags is not None:
            params['tags'] = tags
        if limit is not None:
            params['limit'] = limit

        resp = self.conn.get('entities', params)
        return _jsonutil.deserialize(resp, Entity)

    def retrieve_entity(self, name):
        """
        :param name: `str` entity name
        :return: :class:`.Entity`
        """
        _check_name(name)
        try:
            resp = self.conn.get('entities/' + quote(name, ''))
        except ServerException as e:
            if e.status_code == 404:
                return None
            else:
                raise e

        return _jsonutil.deserialize(resp, Entity)

    def create_or_replace_entity(self, entity):
        """
        :param entity: :class:`.Entity`
        :return: True if success
        """
        self.conn.put('entities/' + quote(entity.name, ''), entity)
        return True

    def update_entity(self, entity):
        """
        :param entity: :class:`.Entity`
        :return: True if success
        """
        self.conn.patch('entities/' + quote(entity.name, ''), entity)
        return True

    def delete_entity(self, entity):
        """
        :param entity: :class:`.Entity`
        :return: True if success
        """
        self.conn.delete('entities/' + quote(entity.name, ''))
        return True


class EntityGroupsService(_Service):
    def retrieve_entity_groups(self, expression=None, tags=None, limit=None):
        """
        :param expression: `str`
        :param tags: `str`
        :param limit: `int`
        :return: `list` of :class:`.EntityGroup` objects
        """
        params = {}
        if expression is not None:
            params['expression'] = expression
        if tags is not None:
            params['tags'] = tags
        if limit is not None:
            params['limit'] = limit

        resp = self.conn.get('entity-groups', params)
        return _jsonutil.deserialize(resp, EntityGroup)

    def retrieve_entity_group(self, name):
        """
        :param name: `str` entity group name
        :return: :class:`.EntityGroup`
        """
        _check_name(name)
        try:
            resp = self.conn.get('entity-groups/' + quote(name, ''))
        except ServerException as e:
            if e.status_code == 404:
                return None
            else:
                raise e

        return _jsonutil.deserialize(resp, EntityGroup)

    def create_or_replace_entity_group(self, group):
        """
        :param group: :class:`.EntityGroup`
        :return: True if success
        """
        self.conn.put('entity-groups/' + quote(group.name, ''), group)
        return True

    def update_entity_group(self, group):
        """
        :param group: :class:`.EntityGroup`
        :return: True if success
        """
        self.conn.patch('entity-groups/' + quote(group.name, ''), group)
        return True

    def delete_entity_group(self, group):
        """
        :param group: :class:`.EntityGroup`
        :return: True if success
        """
        self.conn.delete('entity-groups/' + quote(group.name, ''))
        return True

    def retrieve_group_entities(self,
                                group_name,
                                active=None,
                                expression=None,
                                tags=None,
                                limit=None):
        """
        :param group_name: `str`
        :param active: `bool`
        :param expression: `str`
        :param tags: `str`
        :param limit: `int`
        :return: `list` of :class:`.Entity` objects
        """
        params = {}
        if active is not None:
            params['active'] = active
        if expression is not None:
            params['expression'] = expression
        if tags is not None:
            params['tags'] = tags
        if limit is not None:
            params['limit'] = limit

        resp = self.conn.get('entity-groups/' + quote(group_name, '') + '/entities',
                             params)
        return _jsonutil.deserialize(resp, Entity)

    def add_group_entities(self, group_name, *entities, **kwargs):
        """
        :param group_name: `str`
        :param entities: :class:`.Entity` objects
        :param kwargs: createEntities=bool
        :return: True if success
        """
        _check_name(group_name)
        add_command = \
            BatchEntitiesCommand.create_add_command(*entities, **kwargs)
        return self.batch_update_group_entities(group_name, add_command)

    def delete_group_entities(self, group_name, *entity_names):
        """
        :param group_name: `str`
        :param entity_names: `str` objects
        :return: True if success
        """
        delete_command = BatchEntitiesCommand.create_delete_command(*entity_names)
        return self.batch_update_group_entities(group_name, delete_command)

    def batch_update_group_entities(self, group_name, *commands):
        """
        :param group_name: `str`
        :param commands: :class:`.BatchEntitiesCommand` objects
        :return: True if success
        """
        commands = [c for c in commands if not c.empty]

        if len(commands):
            self.conn.patch('entity-groups/' + quote(group_name, '') + '/entities', commands)
            return True
        return False
