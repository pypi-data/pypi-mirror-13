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
import inspect

try:
    unicode = unicode
except NameError:
    unicode = str


def serialize(o):
    if isinstance(o, dict):
        res = {}
        for key in o:
            res[key] = serialize(o[key])
        return res
    if isinstance(o, (list, tuple)):
        return [serialize(el) for el in o]
    if isinstance(o, (str, unicode, numbers.Number, bool)):
        return o
    if o is None:
        return None
    try:
        return o.serialize()
    except AttributeError:
        raise ValueError(unicode(o) + ' could not be serialised')


def deserialize(o, model_class):
    if isinstance(o, (list, tuple)):
        return [deserialize(el, model_class) for el in o]

    try:
        args = inspect.getargspec(model_class.__init__).args
        args.remove('self')

        params = {}
        for attr in o:
            if attr in args:
                params[attr] = o[attr]

        res = model_class(**params)
        for attr in o:
            if attr not in args:
                setattr(res, attr, o[attr])

    except:
        raise ValueError(unicode(o)
                         + ' could not be deserialized to '
                         + unicode(model_class))

    return res


def _getprop(model, prop):
    """
    :raises: :class:`.AttributeError` in case of no prop found
    :param model:
    :param prop: prop name
    :return: prop value
    """
    try:
        # try to get strictly used prop
        attr = model.__dict__[prop]
    except KeyError:
        # try to get private if setter/getter is used
        attr = getattr(model, '_' + prop)

    if attr is None:
        raise AttributeError

    try:
        return attr.serialize()
    except AttributeError:
        return attr


class Serializable(object):
    """
    implements default ``serialize()`` method
    """

    def serialize(self):
        """serialize model to json-serializable object
        keys: object __init__ args, values: not None object props

        :return: json-serializable object
        """
        data = {}
        props = inspect.getargspec(type(self).__init__).args
        props.remove('self')

        for prop in props:
            try:
                data[prop] = _getprop(self, prop)
            except AttributeError:
                pass

        return data
