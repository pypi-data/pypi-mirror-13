#
# Copyright (c) 2011, 2013, 2014, 2015
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
import uuid
from coils.core import \
    Task, Folder, Document, CoilsException, BLOBManager, \
    CoilsUnreachableCode, ServerDefaultsManager, Project, \
    get_yaml_struct_from_project7000, NoSuchPathException, \
    Enterprise, PropertyManager
from coils.net import PathObject
from namedattachment import NamedAttachment


OGO_COILS_NAMESPACE = '57c7fc84-3cea-417d-af54-b659eb87a046'


class EntityObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        self.request = None
        self.parameters = None
        PathObject.__init__(self, parent, **params)

    def _resolve_project_and_path_from_task(self, task):
        '''
        If the target of the AttachFS PUT is a Task then the target of the
        PUT becomes the project the task is currently assigned to.  If the
        task is not associated with a project then an exceptionis raised.
        The return of this function is a triple:

            new-target (the project), possible subdirectory name, \
                a list-containing-the-old-target

        A potential subdirectory name is returned in case inbox subfolder
        mode is enabled.  This allows INBOX support to keep the documents of
        each task isolated rather than having one big pile of documents that
        have been uploaded over time.

        :param task: the task which is the target of the PUT

        Returns:
           target project, subfolder name, link target(s),
           dictionary of object properties,
           log messages to apply to new document
        '''

        document_properties = dict()
        document_properties[
            '{{{0}}}documentOrigin'.format(OGO_COILS_NAMESPACE, )
        ] = 'taskDocument'
        document_properties[
            '{{{0}}}inboxUpload'.format(OGO_COILS_NAMESPACE, )
        ] = 'YES'

        if isinstance(task, Task):
            # The target is a Task, so we default to the Tasks' project
            if task.project:
                target = task.project
                self.log.debug(
                    'Upload target is project assigned task; '
                    'redirecting to OGo#{0} [Project]'.
                    format(target.object_id, ))
            else:
                raise CoilsException(
                    'OGo#{0} [Task] not assigned to a project, '
                    'documents cannot be uploaded'.
                    format(task.object_id, ))
        else:
            raise CoilsException(
                '_resovle_project_and_path_from_task called when'
                'input entity is not a Task!')
        return (
            target,
            'OGo{0}'.format(task.object_id, ),
            [task, ],
            document_properties,  # Object Properties
            [
                'Uploaded to project via task OGo#{0}'.format(task.object_id),
            ]  # Log Messages
        )

    def _resolve_project_and_path_from_enterprise(self, enterprise, ):
        """
        Store a document in the INBOX folder a project associated with an
        Enterprise

        :param enterprise: the enterprise which is the target of the PUT

        Returns:
           target project, subfolder name, link target(s),
           dictionary of object properties,
           log messages to apply to new document
        """

        #
        #  Enterprise document properties
        #
        sd = ServerDefaultsManager()
        document_properties = sd.default_as_dict(
            'EnterpriseDocumentINBOXProperties',
        )
        if not isinstance(document_properties, dict):
            document_properties = dict()
        tmp = dict()
        if document_properties:
            # Do not modify document_properties with loop!
            for key, value in document_properties.items():
                # if the value specified for the enterprise document property
                # starts with a "$" it is replaced with the value from the
                # enterprise object for the specified attribute
                if value.startswith('$'):
                    key_attr = value[1:].lower()
                    if hasattr(enterprise, key_attr):
                        value = getattr(enterprise, key_attr)
                        if value:
                            tmp[key] = value
                        else:
                            self.log.debug(
                                'Enterprise OGo#{0} attribute "{0}" is NULL, '
                                'object property will not be set.'
                                .format(enterprise.object_id, key_attr, key, )
                            )
                    else:
                        self.log.error(
                            'Enterprise OGo#{0} has no attribute "{0}" to '
                            'populate Enterprise Document property "{1}", '
                            'object property will not be set.'
                            .format(enterprise.object_id, key_attr, key, )
                        )
                else:
                    tmp[key] = document_properties[key]
        # replace document_properties with value generated in loop
        document_properties = tmp
        document_properties[
            '{{{0}}}documentOrigin'.format(OGO_COILS_NAMESPACE, )
        ] = 'enterpriseDocument'
        document_properties[
            '{{{0}}}inboxUpload'.format(OGO_COILS_NAMESPACE, )
        ] = 'YES'
        self.log.debug(
            '{0} object properties specified for new Enterprise Document'
            .format(len(document_properties), )
        )

        #
        # find or create project
        #
        project_kind = self.parameters.get('projectKind', None)
        if project_kind:
            projects = self.context.run_command(
                'enterprise::get-projects',
                enterprise=enterprise,
                kind=','.join(project_kind),
            )
        else:
            projects = self.context.run_command(
                'enterprise::get-projects', enterprise=enterprise,
            )
        if not projects:
            # Create project to receive document
            project_kind = project_kind[0] if project_kind else None
            project = self.context.run_command(
                'project::new',
                values={
                    'name': enterprise.name,
                    'kind': project_kind,
                },
            )
            # Assign enterprise to project
            self.context.run_command(
                'project::set-enterprises',
                project=project,
                enterprise_ids=[enterprise.object_id, ],
            )
            # Copy ACLs from Enterprise to project
            for acl in enterprise.acls:
                if not acl.action == 'allowed':
                    continue
                self.context.run_command(
                    'object::set-acl',
                    object=project,
                    context_id=acl.context_id,
                    permissions=acl.permissions,
                )
        else:
            project = projects[0]

        if not project:
            raise NoSuchPathException(
                'No project exists to receive Enterprise document'
            )

        return (
            project,  # target Project
            'OGo{0}'.format(enterprise.object_id, ),  # Subfolder name
            [enterprise, ],  # Link Targets
            document_properties,  # Properties
            [
                'Uploaded to project via enterprise OGo#{0}'
                .format(enterprise.object_id),
            ]  # Log Messages # Log messages
        )

    def _resolve_inbox_target_for_project(self, project, sub_directory_name):
        '''
        If the target of the AttachFS PUT is a project then we need to
        determine what folder in the project should be.  The basic default
        is just to use the root folder - the server by default has no
        understanding of the folder structure within a problem.  Alternatively
        a server-wide fault "ProjectINBOXFolderPath" can be set, this will try
        to drive uploaded documents into the specified path.  For example if
        the "ProjectINBOXFolderPath" is set to a value of "INBOX" then uploads
        will be directed to the project folder "/INBOX". Upon upload this
        folder will be created (permissions permitting) if it does not exist.
        Above and beyond the server default an object property may be set on
        the project to specicially control the upload folder for just that
        project.

            {57c7fc84-3cea-417d-af54-b659eb87a046}inboxPath = "myProjectsInbox"

        Also within the INBOX a subfolder can be created based upon the upload
        target; this can isolate documents uploaded for each task, for example.
        [Uploads to tasks 'bounce' into their associated projects].  This is
        controlled server-side via a server default named
        ProjectINBOXSubdirEnabled; if this default is YES then INBOX
        subfoldering is enabled.  Specific projects can toggle subfoldering on
        and off using an object property in the Coils namespace named
        useINBOXSubfolders.  If the indicated subfolder does not exist and
        subfolder mode is enabled the folder will be created [permissions
        permitting].

           {57c7fc84-3cea-417d-af54-b659eb87a046}useINBOXSubfolders = YES|NO

        This methd is called by _resolve_folder_from_project

        :param project: The project which the upload is targetted.
        :param sub_directory_name: The name of the subdirectory to use or
            create if inbox subfoldering is enabled.
        '''

        sd = ServerDefaultsManager()

        inbox_folder_path = sd.string_for_default('ProjectINBOXFolderPath', '')
        prop = \
            self.context.pm.get_property(
                project, OGO_COILS_NAMESPACE, 'inboxPath',
            )
        if prop:
            inbox_folder_path = prop.get_value()

        sub_directory_mode = \
            sd.bool_for_default('ProjectINBOXSubdirEnabled')
        prop = \
            self.context.pm.get_property(
                project, OGO_COILS_NAMESPACE, 'useINBOXSubfolders',
            )
        if prop:
            if prop.get_value() == 'YES':
                sub_directory_mode = True
            else:
                sub_directory_mode = False

        if inbox_folder_path:
            if sub_directory_mode and sub_directory_name:
                inbox_folder_path = \
                    '{0}/{1}'.format(inbox_folder_path, sub_directory_name, )
            if not inbox_folder_path.startswith('/'):
                inbox_folder_path = '/{0}'.format(inbox_folder_path, )

        return inbox_folder_path

    def _resolve_folder_from_project(
        self,
        project,
        sub_directory_name,
    ):
        '''
        If the target of the AttachFS is a project then use the
        resolve_inbox_target_for_project to determine then find
        or create that folder.

        :param project: The project which is the target of the AttachFS upload
        :param sub_directory_name:
        '''
        target = None
        if isinstance(project, Project):
            folder_path = \
                self._resolve_inbox_target_for_project(
                    project, sub_directory_name,
                )
            self.log.debug(
                'Using INBOX Folder path of "{0}"'.format(folder_path, )
            )
            target = self.context.run_command(
                'project::get-path',
                path=folder_path,
                project=project,
                create=True,
            )
        else:
            raise CoilsException(
                'resolve_folder_from_project called when target '
                'is not a Project')
        if not isinstance(target, Folder):
            raise CoilsException(
                'Unable to resolve target folder from project.')
        return target, folder_path, None

    def _put_photo_mode(self, name, scratch_file, mimetype):
        """
        handle and upload in photo mode

        :param name: The name of the file upload
        :param scratch_file: The stream file containing the contents
            of the upload
        :param mimetype: The content-type specified by the client
        """

        # TODO: should be check the filesize here?

        self.context.run_command(
            'contact::set-photo',
            handle=scratch_file,
            mimetype=mimetype,
            contact=self.entity,
        )

        # Respond to client
        self.context.commit()
        self.request.simple_response(
            201,
            mimetype=mimetype,
            headers={
                'X-OpenGroupware-Contact-Id': str(self.entity.object_id),
                'Content-Type': mimetype,
            },
        )

    def _put_file_mode(self, name, scratch_file, mimetype):
        '''
        Handle an upload in file (document) mode.

        :param name: The name of the file upload
        :param scratch_file: The stream file containing the contents
            of the upload
        :param mimetype: The content-type specified by the client
        '''

        object_links = []
        object_properties = None
        log_messages = None

        #
        # Special handling for creating or updating document content
        # via AttachFS
        #
        document = None
        sub_directory_name = None

        if isinstance(self.entity, Task):
            (
                self.entity, sub_directory_name, link_sources,
                object_properties, log_messages,
            ) = self._resolve_project_and_path_from_task(self.entity)
            if link_sources:
                object_links.extend(link_sources)
        elif isinstance(self.entity, Enterprise):
            (
                self.entity, sub_directory_name, link_sources,
                object_properties, log_messages
            ) = self._resolve_project_and_path_from_enterprise(self.entity)
            if link_sources:
                object_links.extend(link_sources)

        if isinstance(self.entity, Project):
            self.entity, sub_directory_name, link_sources, = \
                self._resolve_folder_from_project(
                    self.entity, sub_directory_name,
                )
            if link_sources:
                object_links.extend(link_sources)

        if isinstance(self.entity, Folder):
            # Determine the target filename.  If none is specified
            # then we make one up; essentially a UUID/GUID with a
            # ".bin" extension.  Although sending file create request
            # without a filename seems stupid.
            if name:
                # BUG: names without extenstions may not work!
                document = self.context.r_c('folder::ls',
                                            id=self.entity.object_id,
                                            name=name, )
                if document:
                    document = document[0]
                    self.log.debug(
                        'Found existing upload target OGo#{0} [{1}]'.
                        format(document.object_id,
                               document.__entityName__, ))
            else:
                # BUG: Just due to URL parsing semantics I belive this code
                #      path is unreachable.  If no target name is provided it
                #      just seems to fall through to attachment mode.
                name = '{0}.bin'.format(uuid.uuid4().hex)
        elif isinstance(self.entity, Document):
            # We already know the file, so we don't need a filename
            # Posting content to a File via AttachFS *always*
            # updates the contents of said file - potentially
            # creating a new version depending on the storage
            # backend
            document = self.entity
        else:
            raise CoilsException(
                'Mode "file" not support by AttachFS for objects of type {0}'.
                format(self.entity))

        action = None  # used later for inserting auto messages for action
        if not document:
            action = '00_created'
            # CREATE DOCUMENT / FILE
            # A matching document was not found, we are going to create
            # a document
            self.log.debug(
                'No document found for upload target, creating document.')
            document = self.context.run_command(
                'document::new',
                name=name,
                values={},
                folder=self.entity,
                handle=scratch_file,
            )
            self.log.debug('OGo#{0} [Document] created via AttachFS upload'.
                           format(document.object_id, ))
            # set object properties on new document
            if object_properties:
                self.log.debug(
                    'Setting {0} object properties on document OGo#{1}'
                    .format(len(object_properties), document.object_id, )
                )
                for key, value in object_properties.items():
                    ns, attribute = PropertyManager.Parse_Property_Name(key)
                    self.context.property_manager.set_property(
                        entity=document,
                        namespace=ns,
                        attribute=attribute,
                        value=value,
                    )
            else:
                self.log.debug(
                    'No object properties to be set on document OGo#{0}'
                    .format(document.object_id, )
                )
        else:
            # UPDATE DOCUMENT / FILE (possibly rename)
            # A document was found [or specified as the target] so we are
            # doing an update
            action = '05_changed'
            if name == '*':
                self.context.r_c('document::set',
                                 object=document,
                                 values={},
                                 handle=scratch_file, )
            else:
                self.context.r_c('document::set',
                                 object=document,
                                 name=name,
                                 values={},
                                 handle=scratch_file, )
            self.log.debug('OGo#{0} [Document] updated via AttachFS upload'.
                           format(document.object_id, ))

        #
        # Store any additional log messages on document
        #
        if log_messages:
            for log_message in log_messages:
                self.context.audit_at_commit(
                    document.object_id,
                    action=action,
                    message=log_message,
                )

        # For best WebDAV compatibility set the expected properties on the
        # document
        self.context.pm.set_property(
            document,
            'http://www.opengroupware.us/mswebdav',
            'isTransient',
            'NO',
        )
        self.context.pm.set_property(
            document,
            'http://www.opengroupware.us/mswebdav',
            'contentType',
            mimetype,
        )

        #
        # Property Aliasing
        #
        aliased_properties = {}

        for key, value in self.parameters.items():
            if key.startswith('pa.'):
                if not value:
                    value = 'YES'
                else:
                    value = value[0]
                aliased_properties[key[3:]] = value
            elif key == 'abstract':
                document.abstract = value[0]
            elif key == 'appointment':
                # TODO: verify appointment id validity?
                document.appointment_id = long(value[0])
            elif key == 'company':
                # TODO: verify company id validity?
                document.company_id = long(value[0])

        if aliased_properties:
            prop_map = get_yaml_struct_from_project7000(
                context=self.context,
                path='/PropertyAliases.yaml',
                access_check=False,
            )
            for alias, value in aliased_properties.items():
                if alias in prop_map:
                    namespace = prop_map[alias]['namespace']
                    attribute = prop_map[alias]['attribute']
                    self.context.pm.set_property(
                        document, namespace, attribute, value,
                    )

        # Generate requested object links, if any

        for source in object_links:
            self.context.link_manager.link(source, document, label=name)
            self.log.debug(
                'Linked OGo#{0} [{1}] to OGo#{2}'.
                format(source.object_id,
                       source.__entityName__,
                       document.object_id, ))

        # Respond to client
        self.context.commit()
        self.request.simple_response(
            201,
            mimetype=mimetype,
            headers={
                'X-OpenGroupware-Document-Id': str(document.object_id),
                'X-OpenGroupware-Folder-Id': str(document.folder_id),
                'Etag': '{0}:{1}'.format(
                    document.object_id,
                    document.version,
                ),
                'Content-Type': document.mimetype,
            },
        )

    def do_HEAD(self):
        mimetype = self.context.type_manager.get_mimetype(self.entity)
        headers = {
            'X-OpenGroupware-ObjectId': str(self.entity.object_id),
            'X-OpenGroupware-Version': str(self.entity.version),
            'Content-Type': mimetype,
        }

        if isinstance(self.entity, Document):
            """Add additional headers to document entity HEAD response"""
            headers.update({
                'X-OpenGroupware-Document-Id': str(self.entity.object_id),
                'X-OpenGroupware-Folder-Id': str(self.entity.folder_id),
                'X-OpenGroupware-Revision': str(self.entity.version_count),
                'X-OpenGroupware-Version': str(self.entity.version),
                'X-OpenGroupware-Checksum': str(self.entity.checksum),
                'X-OpenGroupware-Project-Id': str(self.entity.project_id),
                'X-OpenGroupware-Folder-Path': '/'.join(
                    self.entity.folder_name_path
                ),
            })
        self.request.simple_response(
            200,
            mimetype=mimetype,
            headers=headers,
        )

    def do_PUT(self, name):
        payload = self.request.get_request_payload()
        mimetype = self.request.headers.get(
            'Content-Type', 'application/octet-stream',
        )
        self.log.debug(
            'Attachment upload MIME type is "{0}"'.format(mimetype, ))
        scratch_file = BLOBManager.ScratchFile()
        scratch_file.write(payload)
        self.log.debug('Wrote {0}b to upload buffer'.
                       format(scratch_file.tell(), ))
        scratch_file.seek(0)
        attachment = None

        # Detect the mode for the operation; we fall through to the
        # default but allow an alternate to be specified via the URL
        # parameter "mode".  Currently mode "file" is supported to
        # easily allow the content of documents [files in projects] to
        # be updated and for documents [files in projects] to be
        # created.
        mode = None
        if 'mode' in self.parameters:
            mode = self.parameters['mode'][0].lower()
        else:
            mode = 'default'

        if mode == 'file':

            self.log.debug('AttachFS upload mode is file/document')
            self._put_file_mode(name, scratch_file, mimetype)
            return

        elif mode == 'photo':

            self.log.debug('AttachFS upload mode is photo')
            self._put_photo_mode(name, scratch_file, mimetype)
            return

        elif mode == 'default':
            #
            # Default AttachFS behavior
            #
            attachment = self.context.run_command(
                'attachment::new',
                handle=scratch_file,
                name=name,
                entity=self.entity,
                mimetype=mimetype,
            )
            self.context.commit()

            if attachment:
                self.request.simple_response(
                    201,
                    mimetype=mimetype,
                    headers={
                        'Etag': attachment.uuid,
                        'Content-Type': attachment.mimetype,
                    },
                )
                return

            else:
                # TODO; Can this happen without an exception having occurred?
                raise CoilsUnreachableCode(
                    'Attachment after attachment::new is NULL'
                )

        raise CoilsException(
            'Unrecognized mode "{0}" specified for AttachFS operation.'.
            format(mode, )
        )

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if name in ('download', 'view', ):
            return NamedAttachment(
                self,
                name,
                entity=self.entity,
                request=self.request,
                parameters=self.parameters,
                context=self.context,
            )
        raise NoSuchPathException(
            'Specify "download" or "view" as subordinates to '
            'AttachFS EntityObject.\n To retrieve an attachment '
            'for an entity the correct path is: '
            '/attachfs/{entityObjectId}/download|view/{attachmentName}.\n'
            'To retrieve an attachment by UUID/GUID simply request: '
            '/attachfs/download|view/{UUID/GUID}\n'
        )
