"""This module contains the general information for AdaptorEthCompQueueProfile ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class AdaptorEthCompQueueProfileConsts():
    pass


class AdaptorEthCompQueueProfile(ManagedObject):
    """This is AdaptorEthCompQueueProfile class."""

    consts = AdaptorEthCompQueueProfileConsts()
    naming_props = set([])

    mo_meta = MoMeta("AdaptorEthCompQueueProfile", "adaptorEthCompQueueProfile", "eth-comp-q", VersionMeta.Version101e, "InputOutput", 0x3fL, [], ["admin", "ls-config-policy", "ls-network", "ls-server-policy"], [u'adaptorHostEthIf', u'adaptorHostEthIfProfile', u'adaptorUsnicConnDef'], [], ["Get", "Set"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version101e, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "count": MoPropertyMeta("count", "count", "ushort", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x4L, None, None, None, [], ["1-512"]), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x8L, 0, 256, None, [], []), 
        "ring_size": MoPropertyMeta("ring_size", "ringSize", "ushort", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, [], ["1-1"]), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x10L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x20L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "count": "count", 
        "dn": "dn", 
        "ringSize": "ring_size", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.count = None
        self.ring_size = None
        self.sacl = None
        self.status = None

        ManagedObject.__init__(self, "AdaptorEthCompQueueProfile", parent_mo_or_dn, **kwargs)

