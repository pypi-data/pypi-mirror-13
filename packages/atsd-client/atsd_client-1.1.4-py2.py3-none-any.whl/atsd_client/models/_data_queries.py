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


import numbers
from datetime import datetime

from ._data_models import Property
from ._data_models import to_posix_timestamp
from .._jsonutil import Serializable
from ._data_models import Alert

try:
    unicode = unicode
except NameError:
    unicode = str


class SeriesType(object):
    HISTORY = 'HISTORY'
    FORECAST = 'FORECAST'
    FORECAST_DEVIATION = 'FORECAST_DEVIATION'


class Interpolate(object):
    NONE = 'NONE'
    LINEAR = 'LINEAR'
    STEP = 'STEP'


class TimeUnit(object):
    MILLISECOND = 'MILLISECOND'
    SECOND = 'SECOND'
    MINUTE = 'MINUTE'
    HOUR = 'HOUR'
    DAY = 'DAY'
    WEEK = 'WEEK'
    MONTH = 'MONTH'
    QUARTER = 'QUARTER'
    YEAR = 'YEAR'


class AggregateType(object):
    DETAIL = 'DETAIL'
    COUNT = 'COUNT'
    MIN = 'MIN'
    MAX = 'MAX'
    AVG = 'AVG'
    SUM = 'SUM'
    PERCENTILE_999 = 'PERCENTILE_999'
    PERCENTILE_995 = 'PERCENTILE_995'
    PERCENTILE_99 = 'PERCENTILE_99'
    PERCENTILE_95 = 'PERCENTILE_95'
    PERCENTILE_90 = 'PERCENTILE_90'
    PERCENTILE_75 = 'PERCENTILE_75'
    PERCENTILE_50 = 'PERCENTILE_50'
    STANDARD_DEVIATION = 'STANDARD_DEVIATION'
    FIRST = 'FIRST'
    LAST = 'LAST'
    DELTA = 'DELTA'
    WAVG = 'WAVG'
    WTAVG = 'WTAVG'
    THRESHOLD_COUNT = 'THRESHOLD_COUNT'
    THRESHOLD_DURATION = 'THRESHOLD_DURATION'
    THRESHOLD_PERCENT = 'THRESHOLD_PERCENT'


class Severity(object):
    UNDEFINED = 0
    UNKNOWN = 1
    NORMAL = 2
    WARNING = 3
    MINOR = 4
    MAJOR = 5
    CRITICAL = 6
    FATAL = 7


class Rate(Serializable):
    def __init__(self, period=None, counter=None):

        #: `dict` {'count': `Number`, 'unit': :class:`.TimeUnit`},
        #: use ``set_period`` method instead setting explicitly
        self.period = period
        #: `bool`
        self.counter = counter

    def set_period(self, count, unit=TimeUnit.SECOND):
        """
        :param count: number
        :param unit: use :class:`.TimeUnit` enum, default TimeUnit.SECOND
        """
        if not isinstance(count, numbers.Number):
            raise ValueError('period count expected number, found: '
                             + unicode(type(count)))
        if not hasattr(TimeUnit, unit):
            raise ValueError('wrong period unit')
        self.period = {'count': count, 'unit': unit}


class Group(Serializable):
    """
    represents aggregate param group
    """
    def __init__(self, type, interpolate=None, truncate=None, period=None):
        #: :class:`.AggregateType`
        self.type = type

        #: :class:`.Interpolate`
        self.interpolate = interpolate
        #: `bool` default False
        self.truncate = truncate
        #: `dict` {'count': `Number`, 'unit': :class:`.TimeUnit`},
        #: use ``set_period`` method instead setting explicitly
        self.period = period

    def set_period(self, count, unit=TimeUnit.SECOND):
        """
        :param count: number
        :param unit: use :class:`.TimeUnit` enum, default TimeUnit.SECOND
        """
        if not isinstance(count, numbers.Number):
            raise ValueError('period count expected number, found: '
                             + unicode(type(count)))
        if not hasattr(TimeUnit, unit):
            raise ValueError('wrong period unit')
        self.period = {'count': count, 'unit': unit}


class Aggregator(Serializable):
    """
    represents aggregate param of :class:`.SeriesQuery`
    """
    def __init__(self, types, period,
                 interpolate=None,
                 threshold=None,
                 calendar=None,
                 workingMinutes=None,
                 counter=None):

        #: `dict` {'count': `Number`, 'unit': :class:`.TimeUnit`},
        #: use ``set_period`` method instead setting explicitly
        self.period = period
        #: `list` of :class:`.AggregateType` objects
        self.types = types

        #: :class:`.Interpolate`
        self.interpolate = interpolate
        #: `dict` {'min': `Number`, 'max': `Number`}
        #: use ``set_threshold`` method instead setting explicitly
        self.threshold = threshold
        #: `dict` {'name': `str`}
        #: use ``set_threshold`` method instead setting explicitly
        self.calendar = calendar
        #: `dict` {'start': `int`, 'end': `int`}
        #: use ``set_workingMinutes`` method instead setting explicitly
        self.workingMinutes = workingMinutes
        #: `bool`
        self.counter = counter

    def set_types(self, *types):
        """specified aggregation types

        :param types: use :class:`.AggregateType` enum objects
        """
        self.types = []
        for typ in types:
            if not hasattr(AggregateType, typ):
                raise ValueError('wrong aggregate type')
            self.types.append(typ)

    def set_period(self, count, unit=TimeUnit.SECOND):
        """
        :param count: number
        :param unit: use :class:`.TimeUnit` enum, default TimeUnit.SECOND
        """
        if not isinstance(count, numbers.Number):
            raise ValueError('period count expected number, found: '
                             + unicode(type(count)))
        if not hasattr(TimeUnit, unit):
            raise ValueError('wrong period unit')
        self.period = {'count': count, 'unit': unit}

    def set_threshold(self, min, max):
        """
        :param min: `Number`
        :param max: `Number`
        """
        self.threshold = {'min': min, 'max': max}

    def set_workingMinutes(self, start, end):
        """
        :param start: `int`
        :param end: `int`
        """
        self.workingMinutes = {'start': start, 'end': end}

    def set_calendar(self, name):
        """
        :param name: `str`
        """
        self.calendar = {'name': name}


class _TimePeriodQuery(Serializable):
    def __init__(self, startTime, endTime):

        if isinstance(startTime, datetime):
            startTime = to_posix_timestamp(startTime)
        #: `long` start of the selection period.
        #: default: ``endTime - 1 hour``
        self._startTime = startTime

        if isinstance(endTime, datetime):
            endTime = to_posix_timestamp(endTime)
        #: `long` end of the selection period.
        #: default value: ``current server time``
        self._endTime = endTime

    @property
    def startTime(self):
        """`datetime` Start of the selection period
        """
        if self._startTime is None:
            return None
        return datetime.fromtimestamp(self._startTime / 1000)

    @startTime.setter
    def startTime(self, value):
        if isinstance(value, numbers.Number):
            self._startTime = value
        elif isinstance(value, datetime):
            self._startTime = to_posix_timestamp(value)
        else:
            raise ValueError('startTime should be either Number or datetime')

    @property
    def endTime(self):
        """ `datetime` End of the selection period
        """
        if self._endTime is None:
            return None
        return datetime.fromtimestamp(self._endTime / 1000)

    @endTime.setter
    def endTime(self, value):
        if isinstance(value, numbers.Number):
            self._endTime = value
        elif isinstance(value, datetime):
            self._endTime = to_posix_timestamp(value)
        else:
            raise ValueError('endTime should be either Number or datetime')


class SeriesQuery(_TimePeriodQuery):
    def rate(self):
        """add empty rate property to series query,
        use returned object methods to set parameters

        :return: :class:`.Rate` object

        Usage::

            >>> query = SeriesQuery(ENTITY, METRIC)
            >>> rate = query.rate()
            >>> rate.counter = False
            >>> series = svc.retrieve_series(query)

        """
        self._rate = Rate()
        return self._rate

    def aggregate(self, *types):
        """add aggregate property to series query, default period = 1 sec
        use returned object methods to set parameters

        :param types: :class:`.InterpolateType` objects
        :return: :class:`.Aggregator` object

        Usage::

            >>> query = SeriesQuery(ENTITY, METRIC)
            >>> aggr = query.aggregate()
            >>> aggr.set_period(10, TimeUnit.DAY)
            >>> aggr.set_types(AggregateType.MAX, AggregateType.MIN)
            >>> series = svc.retrieve_series(query)

        """

        self._aggregate = Aggregator(types,
                                     {'count': 1, 'unit': TimeUnit.SECOND})
        return self._aggregate

    def group(self, type):
        """add group property to series query
        use returned object methods to set parameters

        :param type: :class:`.AggregateType` enum
        :return: :class:`.Group` object

        Usage::

            >>> query = SeriesQuery(ENTITY, METRIC)
            >>> group = query.group(AggregateType.COUNT)
            >>> group.set_period(1, TimeUnit.SECOND)
            >>> series = svc.retrieve_series(query)

        """
        self._group = Group(type)
        return self._group

    def __init__(self, entity, metric,
                 startTime=None,
                 endTime=None,
                 limit=None,
                 last=None,
                 tags=None,
                 type=None,
                 group=None,
                 rate=None,
                 aggregate=None,
                 requestId=None,
                 versioned=None):
        #: `str` entity name
        self.entity = entity
        #: `str` metric name
        self.metric = metric

        #: `int` maximum number of data samples returned
        self.limit = limit
        #: `bool` Retrieves only 1 most recent value
        self.last = last
        #: `dict`
        self.tags = tags
        #: :class:`.SeriesType`
        self.type = type
        self._group = group
        self._rate = rate
        self._aggregate = aggregate
        #: `str`
        self.requestId = requestId
        #: `boolean`
        self.versioned = versioned

        super(SeriesQuery, self).__init__(startTime, endTime)


class PropertiesQuery(_TimePeriodQuery):
    def __init__(self, type, entity,
                 startTime=None,
                 endTime=None,
                 limit=None,
                 key=None,
                 keyExpression=None):
        #: `str` entity name
        self.entity = entity
        #: `str` type of data properties
        self.type = type

        #: `int` maximum number of data samples returned.
        #: default value: 0 (no limit)
        self.limit = limit
        #: `dict` of ``name: value`` pairs that uniquely identify
        #: the property record
        self.key = key
        #: `str`
        self.keyExpression = keyExpression

        super(PropertiesQuery, self).__init__(startTime, endTime)


class PropertiesMatcher(Serializable):
    def __init__(self, type,
                 entity=None,
                 key=None,
                 createdBeforeTime=None):
        #: `str`
        self.type = type

        #: `str`
        self.entity = entity
        #: `dict`
        self.key = key
        #: `long` milliseconds
        self.createdBeforeTime = createdBeforeTime


class AlertsQuery(Serializable):
    def __init__(self,
                 metrics=None,
                 entities=None,
                 rules=None,
                 severities=None,
                 minSeverity=None):
        #: `list` of metric names
        self.metrics = metrics
        #: `list` of entity names
        self.entities = entities
        #: `list` of rules
        self.rules = rules
        #: `list` of :class:`.Severity` objects
        self.severities = severities
        #: :class:`.Severity`
        self.minSeverity = minSeverity


class AlertHistoryQuery(_TimePeriodQuery):
    def __init__(self, entity, metric, startTime, endTime, rule,
                 entityGroup=None,
                 limit=None):
        #: `str` entity name
        self.entity = entity
        #: `str` metric name
        self.metric = metric
        #: `str`
        self.rule = rule

        #: `str`
        self.entityGroup = entityGroup
        #: `int`, default 1000
        self.limit = limit

        super(AlertHistoryQuery, self).__init__(startTime, endTime)


class BatchPropertyCommand(object):
    def __init__(self, action, properties=None, matchers=None):
        self.action = action
        if properties:
            if len(properties) is 0:
                self.empty = True
            self.properties = properties
            self._properties_data = [p.serialize() for p in properties]
        else:
            if len(matchers) is 0:
                self.empty = True
            self.matchers = matchers
            self._matchers_data = [m.serialize() for m in matchers]
        self.empty = False

    def serialize(self):
        data = {'action': self.action}
        try:
            data['properties'] = self._properties_data
        except AttributeError:
            data['matchers'] = self._matchers_data

        return data

    @staticmethod
    def create_insert_command(*insertions):
        """
        :param insertions: :class:`.Property` objects
        :return: :class:`BatchPropertyCommand` instance
        """
        for insertion in insertions:
            if not isinstance(insertion, Property):
                raise TypeError('expected:' + repr(Property)
                                + ', found:' + repr(type(insertion)))

        return BatchPropertyCommand('insert', properties=insertions)

    @staticmethod
    def create_delete_command(type, entity, key=None):
        """
        :param type: `str`
        :param entity: `str`
        :param key: `dict`
        :return: :class:`BatchPropertyCommand` instance
        """
        prop = Property(type, entity, {})
        if key is not None:
            prop.key = key
        return BatchPropertyCommand('delete', properties=(prop,))

    @staticmethod
    def create_delete_match_command(*matchers):
        """
        :param matchers: :class:`.PropertiesMatcher` objects
        :return: :class:`BatchPropertyCommand` instance
        """
        for matcher in matchers:
            if not isinstance(matcher, PropertiesMatcher):
                raise TypeError('expected:' + repr(PropertiesMatcher)
                                + ', found:' + repr(type(matcher)))

        return BatchPropertyCommand('delete-match', matchers=matchers)


class BatchAlertCommand(object):
    def __init__(self, action, alerts, fields=None):
        if len(alerts) is 0:
            self.empty = True
            return

        self.empty = False
        self.action = action
        self.alerts = alerts
        self.fields = fields
        self._data_alerts = [alert.serialize() for alert in alerts]

    def serialize(self):
        return {
            'action': self.action,
            'alerts': self._data_alerts,
            'fields': self.fields
        }

    @staticmethod
    def create_delete_command(*alert_ids):
        """
        :param alert_ids: str
        :return: :class:`.BatchAlertCommand` instance
        """
        return BatchAlertCommand('delete',
                                 alerts=[Alert(i) for i in alert_ids])

    @staticmethod
    def create_update_command(acknowledge, *alert_ids):
        """
        :param acknowledge: `boolean`
        :param alert_ids: str
        :return: :class:`.BatchAlertCommand` instance
        """
        return BatchAlertCommand('update',
                                 alerts=[Alert(id) for id in alert_ids],
                                 fields={'acknowledge': acknowledge})
