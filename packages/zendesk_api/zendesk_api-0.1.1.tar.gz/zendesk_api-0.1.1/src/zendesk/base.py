#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Zendesk API
# Copyright (c) 2008-2015 Hive Solutions Lda.
#
# This file is part of Hive Zendesk API.
#
# Hive Zendesk API is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Zendesk API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Zendesk API. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2015 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import base64

import appier

from . import user
from . import ticket

DOMAIN = "https://www.googleapis.com/"
""" The default base url to be used when no other
base url value is provided to the constructor """

class Api(
    appier.OAuth2Api,
    user.UserApi,
    ticket.TicketApi
):

    def __init__(self, *args, **kwargs):
        appier.Api.__init__(self, *args, **kwargs)
        self.client_id = appier.conf("ZD_DOMAIN", DOMAIN)
        self.username = appier.conf("ZD_USERNAME", None)
        self.password = appier.conf("ZD_PASSWORD", None)

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        auth = kwargs.pop("auth", True)
        if auth: headers["Authorization"] = self.get_authorization()

    def get_authorization(self):
        if not self.username or not self.password: None
        payload = "%s/token:%s" % (self.username, self.password)
        payload = appier.legacy.bytes(payload)
        authorization = base64.b64encode(payload)
        authorization = appier.legacy.str(authorization)
        return "Basic %s" % authorization
