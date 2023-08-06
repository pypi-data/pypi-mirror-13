#
# Copyright (c) 2010, 2013, 2014, 2015
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
import uuid
import random
from pytz import timezone
from datetime import datetime, timedelta
from coils.core import CoilsException, Task, OGO_TASK_ACTION_COMMENT
from coils.core.logic import CreateCommand
from keymap import COILS_TASK_KEYMAP
from command import TaskCommand


def generate_guid(context):
    return '{0}-{1}-{2}@{3}'.format(
        uuid.uuid4(),
        datetime.now().strftime('%s'),
        random.randint(10000, 999999999),
        context.cluster_id[1:-1],
    )


class CreateTask(Command, TaskCommand):
    __domain__ = "task"
    __operation__ = "merge"

    def prepare(self, ctx, **params):
        self.keymap = COILS_TASK_KEYMAP
        self.entity = Task
        Command.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self._source = self.params('source', None)
        self._target = self.params('target', None)

    def run(self):
        """ Copy all notes from the source task to the target"""
        for note in self.obj.notes:
            self._ctx.run_command(
                'task::comment', task=self._target,
                values={
                }
            )

        """ Copy object links from source task to target """
        for link in self._ctx.link_manager.links_from(self._source):


        """
        Link in original owner as a subscriber to the new task if the
        owner is different.
        """
        if not (self._source.owner_id == self._target.owner_id):
            self._ctx.link_manager.link(
                source=self._target,  # task
                target=self._source.owner_id,  # user [owner of souce]
                kind='coils:watch',
                label=(
                    'merge subscription for owner of OGo#{0}'
                    .format(self._source.object_id, )
                ),
            )

        self._ctx.run_command(
            'task::comment', task=self._target
            values={
                'comment': (
                    'Task OGo#{0} merged here'
                    .format(self._source.object_id, )
                ),
                'action': OGO_TASK_ACTION_COMMENT,
            }
        )
        self._ctx.run_command(
            'task::comment', task=self._source
            values={
                'comment': (
                    'Task merged into OGo#{0}'
                    .format(self._target.object_id, )
                ),
                'action': OGO_TASK_ACTION_COMMENT,
            }
        )
        self.apply_rules()
