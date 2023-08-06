
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
# THE SOFTWARE.
#
import re
from datetime import date, timedelta, datetime
from coils.core import \
    walk_ogo_uri_to_folder, \
    Team, \
    get_yaml_struct_from_project7000


RE_DATE_PATTERN = re.compile(r'''\${TODAY-(?P<days>[0-9]*?)};''')


def process_policy(context, uri, policy, ):

    start, _ = walk_ogo_uri_to_folder(
        context=context,
        uri=uri,
        create_path=False,
        default_params=None,
    )
    if start:
        policy.search_criteria.append(
            {
                'expression': 'EQUALS',
                'value': start.object_id,
                'conjunction': 'AND',
                'key': 'topfolderid',
            }
        )
        candidates = context.run_command(
            'document::search',
            criteria=policy.search_criteria,
            limit=4096,
        )
        for candidate in candidates:
            if policy.match_document(candidate):
                policy.perform(
                    context=context,
                    document=candidate,
                )
    else:
        policy.log.info(
            'URI "{0}" does not resolve to a path'.format(uri, )
        )


def parse_value(value):
    global RE_DATE_PATTERN

    if isinstance(value, basestring):
        match = re.match(RE_DATE_PATTERN, value)
        if match:
            value = datetime.now() - timedelta(days=int(match.group('days')))
        elif value.startswith('{DATE:'):
            value = value[6:-1]
            value = datetime.strptime(value, '%Y-%m-%d')
    return value


class DataRetentionPolicy(object):

    @staticmethod
    def Factory(policy_d, name, logger=None, ):

        desc = {
            'searchCriteria': list(),
            'additionalCriteria': {'filename': None, },
            'action': {},
        }

        # Criteria, all candidates are evaluated against these criterion
        desc['additionalCriteria'].update(
            policy_d.get(
                'policyDefaults', {'additionalCriteria': {}, },
            ).get('additionalCriteria'))
        if 'additionalCriteria' in policy_d['policies'][name]:
            desc['additionalCriteria'].update(
                policy_d['policies'][name]['additionalCriteria'])

        # Actions, these actions will be performed on matching candidates
        desc['action'].update(
            policy_d.get(
                'policyDefaults', {'action': {}, },).get('action'))
        if 'action' in policy_d['policies'][name]:
            desc['action'].update(
                policy_d['policies'][name]['action'])

        # Search criteria for identifying candidates
        for criterion in policy_d['policies'][name].get('searchCriteria', []):
            desc['searchCriteria'].append(
                {
                    'key': criterion.get('key'),
                    'conjunction': 'AND',
                    'expression': criterion.get('expression', 'EQUALS'),
                    'value': parse_value(criterion.get('value'), ),
                }
            )

        policy = DataRetentionPolicy(name, desc, logger)
        return policy

    def __init__(self, name, desc, logger):
        self.desc = desc
        self.name = name
        self.log = logger

    def compile(self, context):

        class ReturnTrue(object):
            def match(self, document):
                return True

        class ReturnFalse(object):
            def match(self, document):
                return False

        class CheckRegex(object):
            def __init__(self, context, pattern):
                self.regex = re.compile(pattern)

            def match(self, document):
                return self.regex.match(document.get_file_name())

        class CheckAge(object):

            def __init__(self, context, maxage):
                self.floor = date.today() - timedelta(days=maxage)

            def match(self, document):
                return (document.created.date() < self.floor)

        class CheckOwner(object):

            def __init__(self, context, owner):

                self.idset = set([])

                obj = None

                if isinstance(owner, basestring):
                    if owner.isdigit():
                        obj = context.type_manager.get_entity(long(owner))
                    else:
                        obj = context.r_c('account::get', login=owner, )
                        if not obj:
                            team = context.r_c('team::get', name=owner, )
                elif isinstance(owner, int) or isinstance(owner, long):
                    obj = context.type_manager.get_entity(owner)

                if obj:
                    self.idset.add(obj.object_id)
                    if isinstance(obj, Team):
                        for member in obj.members:
                            self.idset.add(member.child_id)

            def match(self, document):
                return (document.owner_id in self.idset)

        match_true = ReturnTrue()
        match_false = ReturnFalse()

        if self.desc['additionalCriteria'].get('filename', None):
            self.regexp = CheckRegex(
                context=context,
                pattern=self.desc['additionalCriteria']['filename'],
            )
        else:
            self.regexp = match_true

        if self.desc['additionalCriteria'].get('owner', False):
            self.owner = CheckOwner(
                context=context,
                owner=self.desc['additionalCriteria']['owner'],
            )
        else:
            self.owner = match_true

        if self.desc['action'].get('maxVersionAge', False):
            self.version_aging = \
                CheckAge(
                    context=context,
                    maxage=self.desc['action']['maxVersionAge'],
                )
        else:
            self.version_aging = None

        self.version_maximum = \
            self.desc['action'].get('maxVersionCount', False)

    def match_document(self, document):
        if (
            self.owner.match(document) and
            self.regexp.match(document)
        ):
            return True
        return False

    def perform(self, context, document):

        if self.desc['action'].get('discard', False):
            self._reap_document(context=context, document=document)
            return

        if self.version_aging:
            self._reap_versions_by_age(
                context=context,
                document=document,
            )
            return

        if self.version_maximum:
            self._reap_versions_by_count(
                context=context,
                document=document,
            )
            return

    def _reap_versions_by_count(self, context, document, ):

        if document.version_count < self.version_maximum:
            '''
            Not enough version of the document have been created, we can
            short-circuit out.
            '''
            return

        floor = document.version_count - self.version_maximum

        versions = context.run_command(
            'document::get-versions',
            document=document,
        )
        for version in versions:
            if version.version == document.version_count:
                # never delete the current versioned copy
                continue
            if version.version < floor:
                context.audit_at_commit(
                    object_id=document.object_id,
                    action='10_commented',
                    message=(
                        'Version {0} deleted due to data-retention '
                        'policy "{1}" [version count]'.
                        format(version.version, self.name, )
                    )
                )
                try:
                    context.run_command(
                        'document::delete-version',
                        document=document,
                        version=version.version,
                    )
                except Exception as exc:
                    self.log.error(
                        'Exception attempting to delete version {0} '
                        '(OGo#{1}) of document OGo#{2} "{3}" from '
                        'project OGo#{4} "{5}"'.
                        format(
                            version.version,
                            version.object_id,
                            document.object_id,
                            document.get_file_name(),
                            document.project.object_id,
                            document.project.number,
                        )
                    )
                    self.log.exception(exc)
                    raise exc

    def _reap_versions_by_age(self, context, document, ):

        if not self.version_aging.match(document):
            '''
            Document is not old enought itself to have expired version.
            We can short-circuit out.
            '''
            return

        versions = context.run_command(
            'document::get-versions',
            document=document,
        )

        for version in versions:
            if version.version == document.version_count:
                # never delete the current versioned copy
                continue
            if self.version_aging.match(version):
                context.audit_at_commit(
                    object_id=document.object_id,
                    action='10_commented',
                    message=(
                        'Version {0} of document deleted due to data-'
                        'retention policy "{1}" [version age]'.
                        format(
                            version.version,
                            self.name,
                        )
                    )
                )
                context.run_command(
                    'document::delete-version',
                    document=document,
                    version=version.version,
                )

    def _reap_document(self, context, document):
        context.audit_at_commit(
            object_id=document.folder.object_id,
            action='10_commented',
            message=(
                'Document OGo#{0} "{1}" deleted due to data-retention '
                'policy "{2}" [document age]'.
                format(
                    document.object_id,
                    document.get_file_name(),
                    self.name,
                )
            )
        )
        context.r_c('document::delete', object=document, )

    @property
    def search_criteria(self):
        return self.desc['searchCriteria']

    def __repr__(self):
        return '<DataRetentionPolicy name="{0}"/>'.format(self.name)


def execute_data_retention_policy(context, log):

    policy_d = get_yaml_struct_from_project7000(
        context=context,
        path='/DataRetention.yaml',
        access_check=False,
    )
    if not policy_d:
        log.info('No data retention policies defined.')
        return

    for key, value in policy_d.items():
        if key.startswith('ogo://'):
            for policy_name in value:
                policy = DataRetentionPolicy.Factory(
                    policy_d=policy_d,
                    name=policy_name,
                    logger=log,
                )
                policy.compile(context=context)
                process_policy(
                    context=context,
                    uri=key,
                    policy=policy,
                )
                context.commit()
