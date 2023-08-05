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

# TODO: connect return Connection(client)

from ._client import Client
from os import path


def connect_url(base_url,
                username,
                password,
                verify=True,
                timeout=None):
    """connect to ATSD using specified parameters

    :param base_url: ATSD url, for example http://atsd_server:8088
    :param username: user name
    :param password: user password
    :param verify: verify ssl certificate (default True)
    :param timeout: request timeout in seconds (default None - no timeout)
    :return: new client instance
    """

    return Client(base_url,
                  username,
                  password,
                  verify,
                  timeout)


def connect(file_name=None):
    """connect to ATSD using parameters specified in file
    (default connection.properties)

    :param file_name: `str`
    """

    if file_name is None:
        file_name = path.join(path.dirname(__file__), 'connection.properties')
    f = open(file_name)

    params = {}
    for line in f:
        k, v = line.split('=')
        params[k.strip()] = v.strip()

    return Client(**params)
