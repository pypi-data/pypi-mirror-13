#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Mailme API
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Mailme API.
#
# Hive Mailme API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Mailme API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Mailme API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier
import mailme

def send(*args, **kwargs):
    api = mailme.Api()
    api.send(kwargs)

if __name__ == "__main__":
    receivers = appier.conf("RECEIVERS", [], cast = list)
    subject = appier.conf("SUBJECT", None)
    title = appier.conf("TITLE", None)
    contents = appier.conf("CONTENTS", None)
    copyright = appier.conf("COPYRIGHT", None)

    kwargs = dict()
    if receivers: kwargs["receivers"] = receivers
    if subject: kwargs["subject"] = subject
    if title: kwargs["title"] = title
    if contents: kwargs["contents"] = contents
    if copyright: kwargs["copyright"] = copyright

    send(**kwargs)
