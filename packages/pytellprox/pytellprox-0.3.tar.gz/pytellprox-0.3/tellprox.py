#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" This module implements a simple Python interface to the Tellprox API """

__author__ = "Christian Bryn"
__copyright__ = "Copyright 2016, Christian Bryn"
__credits__ = ["Christian Bryn"]
__license__ = "GPLv2"
__version__ = "0.2"
__maintainer__ = "Christian Bryn"
__email__ = "chr.bryn@gmail.com"
__status__ = "Production"


import requests

DEBUG=False

class TellProx():
  def __init__(protocol='http', port='8080', host):
    self.host = host
    self.port = port
    self.protocol = protocol

  def toggle_device(self, id):
    isnum = id
    try:
      isnum += 1
    except TypeError:
      return False
    payload = {'id': id}
    r = requests.get('%s://%s:%s/json/device/toggle?key=&id=%s' % (self.protocol, self.host, self.port, id))
    if DEBUG:
      print(r.url)
    # I think the response needs parsing...but let's assume this works:
    if r.status_code == requests.codes.ok:
      return True
    return False

  def enable_device(self, id):
    isnum = id
    try:
      isnum += 1
    except TypeError:
      return False
    payload = {'id': id}
    r = requests.get('%s://%s:%s/json/device/turnon?key=&id=%s' % (self.protocol, self.host, self.port, id))
    if DEBUG:
      print(r.url)
    # I think the response needs parsing...but let's assume this works:
    if r.status_code == requests.codes.ok:
      return True
    return False

  def disable_device(self, id):
    isnum = id
    try:
      isnum += 1
    except TypeError:
      return False
    payload = {'id': id}
    r = requests.get('%s://%s:%s/json/device/turnoff?key=&id=%s' % (self.protocol, self.host, self.port, id))
    if DEBUG:
      print(r.url)
    # I think the response needs parsing...but let's assume this works:
    if r.status_code == requests.codes.ok:
      return True
    return False

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
