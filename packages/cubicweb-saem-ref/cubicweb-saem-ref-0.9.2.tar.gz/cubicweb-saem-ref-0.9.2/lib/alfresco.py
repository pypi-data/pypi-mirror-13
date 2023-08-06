# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""This module holds Cubicweb independant code easing access to Alfresco (http://www.alfresco.com/)
"""
import sys
import json
from urlparse import urlparse, urljoin

import requests

_ = unicode


class AlfrescoRESTHelper(object):
    """Helper class to access to Alfresco's REST API"""

    def __init__(self, connector):
        assert urlparse(connector.url).scheme == 'http'
        self.url = connector.url
        if not self.url.endswith('/'):
            self.url += '/'
        self.sedaprofiles_node = connector.sedaprofiles_node
        self._ticket = None

    def login(self, user, pwd):
        """Login to the Alfresco API to retrieve a ticket that will be used in subsequent requests.

        POST /alfresco/service/api/login
        INPUT
          {'username': user, 'password': pwd}
        OUTPUT
          {u'data': {u'ticket': u'TICKET_078e228a116a8503c3653ed81de6c7e399860a68'}}

        http://docs.alfresco.com/4.2/references/RESTful-RepositoryLoginPost.html
        """
        data = {'username': user, 'password': pwd}
        res = self._request('POST', 'api/login', json_=data)
        self._ticket = res['data']['ticket']

    def add_sedaprofile(self, fname, file_content):
        """Add an archive profile description file containing `file_content` string

        The file will be uploaded in the SEDA Profile directory, whose node reference must be
        indicated in the sedaprofiles_node parameter of the Alfresco connector.

        :returns: node reference of the new file
            (workspace://SpacesStore/a874ee47-c076-4643-abf6-82cfe8e4aba0 in the example below)

        POST /alfresco/service/api/upload
        INPUT:
            {'filedata', (mandatory) HTML type file,
             'destination', where to store file_content (file stream)
             }
        OUTPUT:
            {"nodeRef": "workspace://SpacesStore/a874ee47-c076-4643-abf6-82cfe8e4aba0",
             "fileName": "filedata-2",
             "status":
                 {
                 "code": 200,
                 "name": "OK",
                 "description": "File uploaded successfully"
                 }
            }
        """
        if not self.sedaprofiles_node:
            raise AlfrescoException('sedaprofiles_node parameter missing in the connector '
                                    'configuration.')
        data = {'destination': 'workspace://SpacesStore/%s' % self.sedaprofiles_node}
        files = {'filedata': (fname, file_content)}
        res = self._request('POST', 'api/upload', data=data, files=files)
        return res['nodeRef']

    def update_sedaprofile(self, fname, file_content, node):
        """Update the archive profile located on node `node` with `file_content` string

        POST /alfresco/service/api/upload
        INPUT:
            {'filedata', (mandatory) HTML type file,
             'updatenoderef', node reference corresponding to the file to update
             }
        OUTPUT:
            {"nodeRef": "workspace://SpacesStore/a874ee47-c076-4643-abf6-82cfe8e4aba0",
             "fileName": "filedata-2",
             "status":
                 {
                 "code": 200,
                 "name": "OK",
                 "description": "File uploaded successfully"
                 }
            }
        """
        data = {'updatenoderef': node}
        files = {'filedata': (fname, file_content)}
        res = self._request('POST', 'api/upload', data=data, files=files)
        return res['nodeRef']

    def add_root_category(self, name):
        """Create a new root category with the given `name`.

        :returns: store reference of the new category
           (workspace://SpacesStore/42587bcd-53f9-4b9f-9e3f-891851484c10 in the example below)

        POST /alfresco/service/api/category
        INPUT:
          {'name': 'this is a test',
           'aspect': '{http://www.alfresco.org/model/content/1.0}generalclassifiable'}
        OUTPUT:
          {'message': u'New category successfully queued with SOLR for addition. Please note that '
                       'it may take a few moments until it is added; you will need to refresh to '
                       'see the change once it has been actioned',
           'persistedObject': u'Node Type: {http://www.alfresco.org/model/content/1.0}categoryNode '
                               'Ref: workspace://SpacesStore/42587bcd-53f9-4b9f-9e3f-891851484c10',
           'name': u'this is a test'}

        http://docs.alfresco.com/4.2/references/RESTful-CategoryCategoryPost.html
        """
        res = self._request('POST', 'api/category', json_={
            'name': name,
            'aspect': '{http://www.alfresco.org/model/content/1.0}generalclassifiable',
        })
        return res['persistedObject'].split('Ref: ', 1)[1]

    def add_sub_category(self, store_ref, name):
        """Create a new sub-category with the given `name` under the `store_ref` node.

        :returns: store reference of the new category
           (workspace://SpacesStore/31aae7d1-9b4a-4e60-9339-ef8e334d01b3 in the example below)

        POST /alfresco/service/api/category/{store_protocol}/{store_id}/{node_id}
        INPUT {'name': 'sub test'}
        OUTPUT
          {'message': u'New category successfully queued with SOLR for addition. Please note that '
                       'it may take a few moments until it is added; you will need to refresh to '
                       'see the change once it has been actioned',
           'persistedObject': u'Node Type: {http://www.alfresco.org/model/content/1.0}categoryNode '
                               'Ref: workspace://SpacesStore/31aae7d1-9b4a-4e60-9339-ef8e334d01b3',
           'name': u'sub test'}

        http://docs.alfresco.com/4.2/references/RESTful-CategoryCategoryPost.html
        """
        store_ref = urlparse(store_ref)
        res = self._request('POST', 'api/category/{0.scheme}/{0.netloc}{0.path}'.format(store_ref),
                            json_={'name': name})
        return res['persistedObject'].split('Ref: ', 1)[1]

    def update_category(self, store_ref, name):
        """Update existing category `store_ref` to a new `name`.

        PUT /alfresco/service/api/category/{store_protocol}/{store_id}/{node_id}
        INPUT {'name': 'new name'}
        OUTPUT
          {'message': u'Category update successfully queued with SOLR for changes. Please note that'
                       ' it may take a few moments until it is updated; you will need to refresh to'
                       ' see the change once it has been actioned',
           'persistedObject': u'Node Type: {http://www.alfresco.org/model/content/1.0}category, '
                               'Node Aspects: [{http://www.alfresco.org/model/content/1.0}auditable, '  # noqa
                               '{http://www.alfresco.org/model/system/1.0}referenceable, '
                               '{http://www.alfresco.org/model/system/1.0}localized]',
           'name': u'new name'}

        http://docs.alfresco.com/4.2/references/RESTful-CategoryCategoryPut.html
        """
        store_ref = urlparse(store_ref)
        self._request('PUT', 'api/category/{0.scheme}/{0.netloc}{0.path}'.format(store_ref),
                      json_={'name': name})

    def delete_category(self, store_ref):
        """Delete existing category `store_ref`. Delete sub-categories recursivly if there are some.

        DELETE /alfresco/service/api/category/{store_protocol}/{store_id}/{node_id}
        OUTPUT
          {'message': u'Category deletion successfully queued with SOLR for removal. Please note '
                       'that it may take a few moments until it is deleted; you will need to '
                       'refresh to see the change once it has been actioned'}

        http://docs.alfresco.com/4.2/references/RESTful-CategoryCategoryDelete.html
        """
        store_ref = urlparse(store_ref)
        self._request('DELETE', 'api/category/{0.scheme}/{0.netloc}{0.path}'.format(store_ref))

    def _request(self, verb, method, data=None, json_=None, files=None):
        request_url = urljoin(self.url, method)
        params = {'alf_ticket': self._ticket}
        try:
            res = requests.request(verb, request_url, params=params, data=data, json=json_,
                                   files=files)
        except requests.ConnectionError as exc:
            raise AlfrescoException(_("can't connect to remote host."))
        if res.status_code // 100 in (4, 5):
            try:
                data = res.json()
            except ValueError:
                message = res.reason
            else:
                message = data.get(u'message', res.reason)
            raise AlfrescoException(message, res.status_code)
        try:
            data = res.json()
        except ValueError as exc:
            context = sys.exc_info()[-1]
            # XXX attempt to read invalid json anyway
            try:
                msg1, msg2 = res.text.split('}{', 1)
            except ValueError:
                raise exc, None, context
            data = json.loads('{' + msg2)
        if data.get('status', {}).get('code', 200) // 100 in (4, 5):
            message = data.get(u'message', res.reason)
            raise AlfrescoException(message, data['status']['code'])
        return data


class AlfrescoException(Exception):
    def __init__(self, message, status=None):
        self.message = message
        self.status = status

    def __str__(self):
        if self.status is not None:
            return '%s: %s' % (self.status, self.message)
        return self.message
