import ldap
import ldif

from ldaptools.utils import idict


class ListLDIFParser(ldif.LDIFParser):
    def __init__(self, *args, **kwargs):
        self.entries = []
        ldif.LDIFParser.__init__(self, *args, **kwargs)

    def handle(self, dn, entry):
        self.entries.append((dn, entry))

    def add(self, conn):
        for dn, entry in self.entries:
            conn.add_s(dn, ldap.modlist.addModlist(entry))

    def __iter__(self):
        for dn, attributes in self.entries:
            yield dn, idict(attributes)
