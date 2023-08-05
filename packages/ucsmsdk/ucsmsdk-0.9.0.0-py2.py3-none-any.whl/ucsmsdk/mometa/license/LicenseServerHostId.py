"""This module contains the general information for LicenseServerHostId ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class LicenseServerHostIdConsts():
    SCOPE_A = "A"
    SCOPE_B = "B"
    SCOPE_SERVER = "server"
    SCOPE_UNKNOWN = "unknown"


class LicenseServerHostId(ManagedObject):
    """This is LicenseServerHostId class."""

    consts = LicenseServerHostIdConsts()
    naming_props = set([u'scope'])

    mo_meta = MoMeta("LicenseServerHostId", "licenseServerHostId", "server-host-id-[scope]", VersionMeta.Version141i, "InputOutput", 0x3fL, [], ["read-only"], [u'licenseEp'], [], ["Get"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version141i, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "host_id": MoPropertyMeta("host_id", "hostId", "string", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, 0x8L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "scope": MoPropertyMeta("scope", "scope", "string", VersionMeta.Version141i, MoPropertyMeta.NAMING, 0x10L, None, None, None, ["A", "B", "server", "unknown"], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version141i, MoPropertyMeta.READ_WRITE, 0x20L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "hostId": "host_id", 
        "rn": "rn", 
        "sacl": "sacl", 
        "scope": "scope", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, scope, **kwargs):
        self._dirty_mask = 0
        self.scope = scope
        self.child_action = None
        self.host_id = None
        self.sacl = None
        self.status = None

        ManagedObject.__init__(self, "LicenseServerHostId", parent_mo_or_dn, **kwargs)

