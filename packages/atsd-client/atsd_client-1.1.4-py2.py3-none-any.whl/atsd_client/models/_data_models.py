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


import time
import numbers
import copy

from datetime import datetime, timedelta

from .._jsonutil import Serializable


class SeriesVersionKey(object):
    """actual version after old versions
    key from comparator
    """

    @staticmethod
    def cmp(a, b):
        if a['t'] == b['t']:
            if ('version' not in a or 't' not in a['version']
                    or 'version' not in b or 't' not in b['version']):
                return 0
            else:
                return a['version']['t'] - b['version']['t']
        else:
            return a['t'] - b['t']

    def __init__(self, obj):
        self.obj = obj

    def __lt__(self, other):
        return SeriesVersionKey.cmp(self.obj, other.obj) < 0

    def __gt__(self, other):
        return SeriesVersionKey.cmp(self.obj, other.obj) > 0

    def __eq__(self, other):
        return SeriesVersionKey.cmp(self.obj, other.obj) == 0

    def __le__(self, other):
        return SeriesVersionKey.cmp(self.obj, other.obj) <= 0

    def __ge__(self, other):
        return SeriesVersionKey.cmp(self.obj, other.obj) >= 0

    def __ne__(self, other):
        return SeriesVersionKey.cmp(self.obj, other.obj) != 0


def _strp(time_str):
    """
    :param time_str: in format '%Y-%m-%dT%H:%M:%SZ%z'
    :return: timestamp in milliseconds
    """
    t, tz = time_str.split('Z')

    t = time.strptime(t, '%Y-%m-%dT%H:%M:%S')

    sig, hour, min = tz[0], tz[1:3], tz[3:5]

    tz_offset = int(sig + hour) * 60 * 60 + int(sig + min) * 60
    loc_offset = time.timezone
    offset = loc_offset - tz_offset

    timestamp = int((time.mktime(t) + offset) * 1000)

    return timestamp


def to_posix_timestamp(dt):
    offset = dt.utcoffset() if dt.utcoffset() is not None else timedelta(seconds=-time.timezone)
    utc_naive = dt.replace(tzinfo=None) - offset
    return int((utc_naive - datetime(1970, 1, 1)).total_seconds() * 1000)


class Property(Serializable):
    def __init__(self, type, entity, tags,
                 key=None,
                 timestamp=None):
        #: `str` property type name
        self.type = type
        #: `str` entity name
        self.entity = entity
        #: `dict` containing object keys
        self.tags = tags

        #: `dict` of ``name: value`` pairs that uniquely identify
        #: the property record
        self.key = key
        #: time in Unix milliseconds
        self.timestamp = timestamp


class Series(Serializable):
    def __init__(self, entity, metric, data=None, tags=None):
        #: `str` entity name
        self.entity = entity
        #: `str` metric name
        self.metric = metric

        # an list of {'t': time, 'v': value} objects
        # use add value instead
        self._data = []
        if data is not None:
            for sample in data:
                sample_copy = copy.deepcopy(sample)
                if sample_copy['v'] == 'NaN':
                    sample_copy['v'] = float('nan')
                self._data.append(sample_copy)

        #: `dict` of ``tag_name: tag_value`` pairs
        self.tags = tags

    def __str__(self):

        if len(self._data) > 20:
            # display only firsts and lasts
            disp_data = self._data[:10] + self._data[-10:]
        else:
            disp_data = self._data

        rows = []
        versioned = False

        # create timestamp and value columns
        for sample in disp_data:
            t = datetime.utcfromtimestamp(sample['t'] * 0.001).strftime('%Y-%m-%dT%H:%M:%SZ')
            v = sample['v']
            row = '{0}{1: >14}'.format(t, v)

            # add version columns
            if 'version' in sample:
                versioned = True
                ver = sample['version']
                src = ver['source'] if 'source' in ver else ''
                sts = ver['status'] if 'status' in ver else ''
                if 't' in ver:
                    t = datetime.utcfromtimestamp(ver['t'] * 0.001).strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    t = ''
                row += '{0: >17}{1: >17}{2: >21}'.format(src, sts, t)

            rows.append(row)

        if versioned:
            # add column names
            header = ('           timestamp'
                      '         value'
                      '   version_source'
                      '   version_status'
                      '         version_time')
            rows.insert(0, header)

        if len(self._data) > 20:
            res = '\n'.join(rows[:-10]) + '\n...\n' + '\n'.join(rows[-10:])
        else:
            res = '\n'.join(rows)

        for key in self.__dict__:
            if not key.startswith('_'):
                res += '\n{0}: {1}'.format(key, getattr(self, key))

        return res

    @staticmethod
    def from_pandas_series(entity, metric, ts):
        """
        :param entity: str entity name
        :param metric: str metric name
        :param ts: pandas time series object
        :return: :class:`.Series` with data from pandas time series
        """
        res = Series(entity, metric)
        for dt in ts.index:
            res.add_value(ts[dt], dt)

        return res

    @property
    def data(self):
        """data getter, use ``add_value()`` method to set values

        :return: an array of {'t': time, 'v': value} objects
        """
        return self._data[:]

    def add_value(self, v, t=None, version=None):
        """add time-value pair to series
        time could be specified as `int` in milliseconds, as `str` in format
        ``%Y-%m-%dT%H:%M:%SZ%z`` (e.g. 2015-04-14T07:03:31Z), as `datetime`

        :param version: `dict`
        :param v: value number
        :param t: `int` | `str` | :class: `.datetime` (default t = current time)
        """
        if t is None:
            t = int(time.time() * 1000)

        if isinstance(t, str):
            t = _strp(t)
        if isinstance(t, datetime):
            t = to_posix_timestamp(t)
        if not isinstance(t, numbers.Number):
            raise ValueError('data "t" should be either number or str')

        if version is None:
            sample = {'v': v, 't': t}
        else:
            sample = {'v': v, 't': t, 'version': version}

        self._data.append(sample)

    def sort(self, key=SeriesVersionKey, reverse=False):
        """sort series data in place

        :param key:
        :param reverse:
        """
        self._data.sort(key=key, reverse=reverse)

    def values(self):
        """valid versions of series values
        :return: [`Number`]
        """

        data = sorted(self._data, key=SeriesVersionKey)
        res = []
        for num, sample in enumerate(data):
            if num > 0 and sample['t'] == data[num - 1]['t']:
                res[-1] = sample['v']
            else:
                res.append(sample['v'])

        return res

    def times(self):
        """valid versions of series times in seconds
        :return: [`float`]
        """

        data = sorted(self._data, key=SeriesVersionKey)

        res = []
        for num, sample in enumerate(data):
            if num > 0 and sample['t'] == data[num - 1]['t']:
                res[-1] = datetime.utcfromtimestamp(sample['t'] * 0.001)
            else:
                res.append(datetime.utcfromtimestamp(sample['t'] * 0.001))

        return res

    def to_pandas_series(self):
        """
        :return: pandas time series object
        """
        import pandas as pd

        return pd.Series(self.values(), index=self.times())

    def plot(self):
        """
        plot series in matplotlib.pyplot
        """
        try:
            return self.to_pandas_series().plot()
        except ImportError:
            import matplotlib.pyplot as plt

            return plt.plot(self.times(), self.values())


class Alert(Serializable):
    def __init__(self, id,
                 rule=None,
                 entity=None,
                 metric=None,
                 lastEventTime=None,
                 openTime=None,
                 value=None,
                 message=None,
                 tags=None,
                 textValue=None,
                 severity=None,
                 repeatCount=None,
                 acknowledged=None,
                 openValue=None):
        self.id = id

        #: `str`
        self.rule = rule
        #: `str`
        self.entity = entity
        #: `str`
        self.metric = metric
        #: `long`
        self.lastEventTime = lastEventTime
        #: `long`
        self.openTime = openTime
        #: `Number`
        self.value = value
        self.message = message
        #: `dict`
        self.tags = tags
        #: `str`
        self.textValue = textValue
        #: :class:`.Severity`
        self.severity = severity
        #: `int`
        self.repeatCount = repeatCount
        #: `bool`
        self.acknowledged = acknowledged
        #: `Number`
        self.openValue = openValue


class AlertHistory(Serializable):
    def __init__(self,
                 alert=None,
                 alertDuration=None,
                 alertOpenTime=None,
                 entity=None,
                 metric=None,
                 receivedTime=None,
                 repeatCount=None,
                 rule=None,
                 ruleExpression=None,
                 ruleFilter=None,
                 schedule=None,
                 severity=None,
                 tags=None,
                 time=None,
                 type=None,
                 value=None,
                 window=None):
        self.alert = alert
        #: `number`
        self.alertDuration = alertDuration
        #: `long` milliseconds
        self.alertOpenTime = alertOpenTime
        #: `str`
        self.entity = entity
        #: `str`
        self.metric = metric
        #: `long` milliseconds
        self.receivedTime = receivedTime
        self.repeatCount = repeatCount
        self.rule = rule
        #: `str`
        self.ruleExpression = ruleExpression
        self.ruleFilter = ruleFilter
        self.schedule = schedule
        self.severity = severity
        #: `dict`
        self.tags = tags
        #: `long` milliseconds
        self.time = time
        self.type = type
        #: `Number`
        self.value = value
        self.window = window

# if __name__ == '__main__':
#     import pandas as pd
#     now = int(time.time() * 1000)
#     dt = datetime.fromtimestamp(now * 0.001)
#     print now, dt, _to_posix_timestamp(dt)
#
#     ts = pd.Series([1], index=[datetime.fromtimestamp(now * 0.001)])
#
#     res = _to_posix_timestamp(ts.index[0])
#     dt = datetime.fromtimestamp(res * 0.001)
#
#     print res, dt