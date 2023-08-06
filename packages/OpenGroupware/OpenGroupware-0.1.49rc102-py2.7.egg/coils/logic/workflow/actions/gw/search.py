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
import json
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from coils.core.xml import Render as XML_Render
from coils.core.omphalos import Render as Omphalos_Render
from coils.foundation import coils_json_encode, coils_yaml_encode


class SearchEntityAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "search-for-entities"
    __aliases__ = ['entitySearchAction', 'entitySearch', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):

        """Search"""
        domain = self._entity_name.lower()
        results = self._ctx.run_command(
            '{0}::search'.format(domain, ),
            criteria=self._search_criteria,
            limit=self._search_limit,
            revolve=self._do_revolve,
        )
        self.log.debug(
            'SearchAction found {0} {1} entities via Logic ::search'
            .format(len(results), self._entity_name, )
        )

        """Write"""

        if self._render_as == 'XML':
            XML_Render.render(
                entity=results,
                ctx=self._ctx,
                detail_level=self._detail_level,
                stream=self.wfile,
            )
            return

        """Non-XML result requested"""

        omphalos = Omphalos_Render.Results(
            results, self._detail_level, self._ctx,
        )

        if self._render_as == 'YAML':
            coils_yaml_encode(omphalos, self.wfile, )
            return

        coils_json_encode(omphalos, self.wfile, )

    @property
    def result_mimetype(self):
        if self._render_as == 'XML':
            return 'application/xml'
        elif self._render_as == 'JSON':
            return 'text/json'
        else:
            return 'text/yaml'

    def parse_action_parameters(self):

        self._search_criteria = json.loads(
            self.process_label_substitutions(
                self.action_parameters.get('criteria', None)
            )
        )

        self._search_limit = int(
            self.process_label_substitutions(
                self.action_parameters.get('limit', '150')
            )
        )

        self._detail_level = int(
            self.process_label_substitutions(
                self.action_parameters.get('detailLevel', '0')
            )
        )

        self._entity_name = self.process_label_substitutions(
            self.action_parameters.get('entityName', None)
        )

        self._do_revolve = 'YES' if (
            self.process_label_substitutions(
                self.action_parameters.get('doRevolve', 'NO')
            ) == 'YES'
        ) else 'NO'

        self._render_as = self.process_label_substitutions(
            self.action_parameters.get('renderAs', 'XML')
        )
        if self._render_as not in ('XML', 'JSON', 'YAML', ):
            raise CoilsException(
                'Unrecognized render target of "{0}", '
                'must be XML, JSON, or YAML'
                .format(self._render_as, )
            )
