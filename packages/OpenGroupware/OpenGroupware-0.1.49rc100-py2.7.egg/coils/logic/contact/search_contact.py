#
# Copyright (c) 2009, 2013, 2015
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
import time
from coils.foundation import apply_orm_hints_to_query
from coils.core import Contact
from coils.logic.address import SearchCompany
from keymap import COILS_CONTACT_KEYMAP

"""
Input:
    criteria = [
        {
            'value':,
            'conjunction':,
            'key':,
            'expression': EQUALS | LIKE | ILIKE,
        } ...
    ]
    limit = #
    debug = True / False
    access_check = True / False
"""


class SearchContacts(SearchCompany):
    __domain__ = "contact"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCompany.__init__(self)

    def prepare(self, ctx, **params):
        SearchCompany.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCompany.parse_parameters(self, **params)

    def add_result(self, contact):
        if (contact not in self._result):
            self._result.append(contact)

    def do_revolve(self):
        enterprises = list()
        for contact in self._result:
            enterprises.extend(
                [assignment.parent_id for assignment in contact.enterprises]
            )
        return self._ctx.run_command(
            'enterprise::get',
            ids=set(enterprises),
            orm_hints=self.orm_hints,
        )

    def run(self):
        self._query = self._parse_criteria(
            self._criteria, Contact, COILS_CONTACT_KEYMAP,
        )
        self._query = \
            apply_orm_hints_to_query(self._query, Contact, self.orm_hints)
        query_start = time.time()
        data = self._query.all()
        self.log.debug(
            'search query returned {0} objects in {1}s'
            .format(len(data), time.time() - query_start, )
        )
        self.set_return_value(data)
        return
