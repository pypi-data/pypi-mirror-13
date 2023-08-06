#
# Copyright (c) 2015
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
from datetime import datetime
from coils.foundation import coils_yaml_encode, coils_yaml_decode
from coils.core import BLOBManager, CoilsException

def get_standardxml_type_name(value):
    if isinstance(value, int) or isinstance(value, long):
        return 'integer'
    if isinstance(value, basestring):
        return 'string'
    if isinstance(value, float):
        return 'float'
    if isinstance(value, datetime):
        return 'datetime'
    return 'unknown'

class WorkflowMap(object):

    def __init__(self, ctx):
        self._context = ctx
        self._document_map = None
        self._rfile = None
        self._wfile = None

    @property
    def map_document(self):
        return self._map_document

    @property
    def rfile(self):
        return self._rfile

    @property
    def wfile(self):
        return self._wfile

    @staticmethod
    def Save(name, data):
        wfile = BLOBManager.Create(
            'wf/maps/{0}.yaml'.format(name, ),
            encoding='binary',
        )
        if wfile is None:
            raise CoilsException(
                'Unable to open Workflow Map "{0}"'.format(name, )
            )
        coils_yaml_encode(data, wfile, allow_none=True, )
        wfile.close()

    @staticmethod
    def Load(name):
        rfile = BLOBManager.Open(
            'wf/maps/{0}.yaml'.format(name, ),
            'rb',
            encoding='binary',
        )
        data = coils_yaml_decode(rfile, allow_none=True, )
        rfile.close()
        return data

    def load(self, name):
        data = WorkflowMap.Load(name)
        self._map_document = data

    def run(self, rfile, wfile):
        pass
