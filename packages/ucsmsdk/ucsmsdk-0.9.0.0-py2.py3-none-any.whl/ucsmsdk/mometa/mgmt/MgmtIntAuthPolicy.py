"""This module contains the general information for MgmtIntAuthPolicy ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class MgmtIntAuthPolicyConsts():
    METHOD_NONE = "none"
    METHOD_PASSWORD = "password"


class MgmtIntAuthPolicy(ManagedObject):
    """This is MgmtIntAuthPolicy class."""

    consts = MgmtIntAuthPolicyConsts()
    naming_props = set([])

    mo_meta = MoMeta("MgmtIntAuthPolicy", "mgmtIntAuthPolicy", "int-mgmt-auth", VersionMeta.Version101e, "InputOutput", 0xffL, [], ["admin", "pn-security"], [u'topSystem'], [], ["Get"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version101e, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "method": MoPropertyMeta("method", "method", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x8L, None, None, None, ["none", "password"], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x10L, 0, 510, None, [], []), 
        "pwd": MoPropertyMeta("pwd", "pwd", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x20L, 0, 510, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x40L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x80L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "method": "method", 
        "name": "name", 
        "pwd": "pwd", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.method = None
        self.name = None
        self.pwd = None
        self.sacl = None
        self.status = None

        ManagedObject.__init__(self, "MgmtIntAuthPolicy", parent_mo_or_dn, **kwargs)

