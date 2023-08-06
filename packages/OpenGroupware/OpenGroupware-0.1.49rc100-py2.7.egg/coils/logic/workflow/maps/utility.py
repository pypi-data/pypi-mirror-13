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
from coils.core import CoilsException
from coils.logic.workflow.maps import WorkflowMap, StandardXMLToHierarchicMap

WORKFLOW_MAP_CLASS = {
    'StandardXMLToHierarchicMap': StandardXMLToHierarchicMap,
}

class NoSuchMapClassException(CoilsException):
    pass

class MapClassInitializationException(CoilsException):
    pass

class MapFactory(object):

    @staticmethod
    def Marshall(context, name):
        map_document = WorkflowMap.Load(name)
        if 'class' not in map_document:
            classname = 'StandardXMLToHierarchicMap'
        else:
            classname = map_document['class']
        map_class = WORKFLOW_MAP_CLASS.get(classname, None)
        if not map_class:
            raise NoSuchMapClassException(
                'No such Map class as "{0}"'
                .format(classname, )
            )
        instance = map_class(context, map_document=map_document)
        instance.name = name
        return instance

