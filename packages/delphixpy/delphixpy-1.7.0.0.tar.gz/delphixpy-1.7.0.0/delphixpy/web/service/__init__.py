#
# Copyright 2016 by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Package "service"
"""
# pylint: disable=W0403,W0611,W0622
API_VERSION = "1.7.0"

from delphixpy.web.service import support
from delphixpy.web.service import security
from delphixpy.web.service import snmp
from delphixpy.web.service import ldap
from delphixpy.web.service import locale
from delphixpy.web.service import schema
from delphixpy.web.service import dns
from delphixpy.web.service import syslog
from delphixpy.web.service import proxy
from delphixpy.web.service import time
from delphixpy.web.service import certificate
from delphixpy.web.service import smtp
from delphixpy.web.service import phonehome
from delphixpy.web.service import linkingsettings
