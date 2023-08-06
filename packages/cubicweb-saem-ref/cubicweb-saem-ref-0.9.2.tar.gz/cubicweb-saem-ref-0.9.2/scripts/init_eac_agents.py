print 'importing some eac files'
import os
import os.path as osp
from cubes.skos.dataimport import SimpleImportLog
EAC_DIR = osp.join(osp.dirname(__file__), os.pardir, 'test', 'data', 'EAC')
for fname in ('FRAD033_EAC_00001.xml', 'FRAD033_EAC_00003.xml', 'FRAD033_EAC_00071.xml'):
    print fname
    import_log = SimpleImportLog(fname)
    cnx.call_service('saem_ref.eac-import', stream=open(osp.join(EAC_DIR, fname)),
                     import_log=import_log, raise_on_error=True)
    cnx.commit()
