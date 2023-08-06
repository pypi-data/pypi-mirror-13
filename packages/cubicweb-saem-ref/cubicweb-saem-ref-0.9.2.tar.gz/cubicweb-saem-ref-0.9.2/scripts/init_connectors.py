
print 'create asalae connector'
asalae = create_entity('AsalaeConnector', url=u'http://localhost/asalae',
                       user=u'admin', password=u'admin',
                       dbhost=u'fulu', dbport=u'5433',
                       database=u'asalae', dbuser=u'asalae')
commit()
print '  visit %s and set proper password' % asalae.absolute_url()

print 'create alfresco connector'
alfresco = create_entity('AlfrescoConnector', url=u'http://dongbi.logilab.priv:8081/alfresco/service',
                         user=u'admin', password=u'fixme', language_code=u'fr',
                         sedaprofiles_node=u'')
print '  visit %s and set proper password' % alfresco.absolute_url()
commit()
