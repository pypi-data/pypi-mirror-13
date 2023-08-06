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
"""cubicweb-saem-ref entity's classes and adapters for Alfresco / As@lae synchronization"""

from cubicweb.entities import AnyEntity

from cubes.skos import to_unicode
from cubes.saem_ref.lib import asalae, alfresco

_ = unicode


class SynchronizationError(Exception):
    """exception used to propage alfresco/asalae exception to the UI"""


class AbstractConnector(AnyEntity):
    __abstract__ = True

    def synchronization_status(self, entity_eid):
        """Return the synchronization status for the given entity's eid, i.e. one of:
        * 'not synchronized', if the entity isn't yet mirrored by this connector,
        * 'not up-to-date', if the entity is mirrored by this connector but needs an update,
        * 'synchronized', if the entity is mirrored by this connector and is up-to-date.
       """
        rset = self._cw.execute(
            'Any MD, XMD, MEF WHERE M mirror_of X, M using_connector C, '
            'M modification_date MD, M error_flag MEF, '
            'X modification_date XMD, X eid %(x)s, C eid %(c)s', {'x': entity_eid, 'c': self.eid})
        if not rset:
            status = _('not synchronized')
        elif rset[0][-1]:
            status = _('synchronization error')
        elif rset[0][1] > rset[0][0]:
            status = _('not up-to-date')
        else:
            status = _('synchronized')
        return status

    def synchronize_blockers(self, eid):
        """Return a list of messages explaining why the given eid may not be synchronized. If an
        empty list is returned, then the entity may be synchronized.
        """
        return ()

    def synchronize(self, eid):
        """Call the relevant service to synchronize the given entity (eid) through the connector.
        """
        raise NotImplementedError()


class AsalaeConnector(AbstractConnector):
    __regid__ = 'AsalaeConnector'

    def dc_title(self):
        return self.url or (u'%s@%s' % (self.database, self.dbhost))

    def synchronize_blockers(self, eid):
        errors = []
        entity = self._cw.entity_from_eid(eid)
        if entity.cw_etype == 'Agent' and entity.kind not in asalae.ASALAE_AGENT_KIND_MAP:
            msg = self._cw._('Agent kind "%s" is not known by As@lae') % entity.printable_kind
            errors.append(msg)
        if entity.cw_etype == 'SEDAProfile':
            pmsg = self._cw._('profile attribute "%s" unspecified')
            for attr in ('title', 'description'):
                if not getattr(entity, attr):
                    errors.append(pmsg % self._cw._(attr))
        return errors

    def synchronize(self, eid):
        def log_and_raise(msg):
            self.exception('error while attempting to synchronize entity %s to asalae using '
                           'connector %s', eid, self.eid)
            raise SynchronizationError(self._cw._(msg))
        try:
            etype = self._cw.entity_metas(eid)['type']
            return self._cw.call_service('saem_ref.asalae.sync-%s' % etype.lower(),
                                         connector_eid=self.eid, eid=eid)
        except asalae.DatabaseConnectionError:
            msg = _('error connecting to Asalae database. Ensure connector settings are correct '
                    'and the Asalae database is reachable.')
            log_and_raise(msg)
        except asalae.DatabaseQueryError:
            msg = _('query error on Asalae database. This might be due to some invalid input, '
                    'a programming error or an invalid database state: check instance log for '
                    'details.')
            log_and_raise(msg)
        except asalae.HostLoginError:
            msg = _('error connecting to Asalae web instance. Ensure user and password connector '
                    'settings are correct.')
            log_and_raise(msg)
        except (asalae.UnknownHostError, asalae.AsalaeConnectionError):
            msg = _('error connecting to Asalae web instance. Ensure connector settings are '
                    'correct and the Asalae web instance is reachable.')
            log_and_raise(msg)
        except asalae.SynchronizationError:
            msg = _('error sending synchronization request to Asalae.')
            log_and_raise(msg)
        except Exception as exc:
            log_and_raise(to_unicode(exc))


class AlfrescoConnector(AbstractConnector):
    __regid__ = 'AlfrescoConnector'

    def synchronize_blockers(self, eid):
        errors = []
        entity = self._cw.entity_from_eid(eid)
        if entity.cw_etype == 'SEDAProfile':
            msg = self._cw._('connector has no "%s" attribute set')
            if not self.sedaprofiles_node:
                errors.append(msg % self._cw._('sedaprofiles_node'))
        return errors

    def synchronize(self, eid):
        try:
            return self._cw.call_service('saem_ref.alfresco.sync', connector_eid=self.eid, eid=eid)
        except alfresco.AlfrescoException as exc:
            self.exception('error on attempt to synchronize entity %s to alfresco using '
                           'connector %s', eid, self.eid)
            _ = self._cw._
            if exc.status == 403:
                msg = _('forbidden changes. Are proper credentials set on the connector? Is the '
                        '"%s" user allowed to edit in the Alfresco instance?')
                msg %= self.user
            elif exc.status == 404:
                msg = _('service not found. Is proper address set on the connector? '
                        'Current is "%s".')
                msg %= self.url
            else:
                msg = _(to_unicode(exc))
            raise SynchronizationError(msg)
