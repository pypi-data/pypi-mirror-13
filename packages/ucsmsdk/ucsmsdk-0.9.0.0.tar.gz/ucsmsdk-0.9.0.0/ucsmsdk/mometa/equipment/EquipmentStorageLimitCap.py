"""This module contains the general information for EquipmentStorageLimitCap ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class EquipmentStorageLimitCapConsts():
    ME4308_SUPPORTED_FALSE = "false"
    ME4308_SUPPORTED_NO = "no"
    ME4308_SUPPORTED_TRUE = "true"
    ME4308_SUPPORTED_YES = "yes"


class EquipmentStorageLimitCap(ManagedObject):
    """This is EquipmentStorageLimitCap class."""

    consts = EquipmentStorageLimitCapConsts()
    naming_props = set([])

    mo_meta = MoMeta("EquipmentStorageLimitCap", "equipmentStorageLimitCap", "storage-limit", VersionMeta.Version251a, "InputOutput", 0x1fL, [], ["read-only"], [u'equipmentLocalDiskControllerCapProvider'], [], ["Get"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version251a, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "max_luns": MoPropertyMeta("max_luns", "maxLuns", "ushort", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "me4308_supported": MoPropertyMeta("me4308_supported", "me4308Supported", "string", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, ["false", "no", "true", "yes"], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, 0x8L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", None, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version251a, MoPropertyMeta.READ_WRITE, 0x10L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "maxLuns": "max_luns", 
        "me4308Supported": "me4308_supported", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.max_luns = None
        self.me4308_supported = None
        self.sacl = None
        self.status = None

        ManagedObject.__init__(self, "EquipmentStorageLimitCap", parent_mo_or_dn, **kwargs)

