"""This module contains the general information for OsARPLinkMonitoringPolicy ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class OsARPLinkMonitoringPolicyConsts():
    USE_ALL_ARPTARGETS_FALSE = "false"
    USE_ALL_ARPTARGETS_NO = "no"
    USE_ALL_ARPTARGETS_TRUE = "true"
    USE_ALL_ARPTARGETS_YES = "yes"


class OsARPLinkMonitoringPolicy(ManagedObject):
    """This is OsARPLinkMonitoringPolicy class."""

    consts = OsARPLinkMonitoringPolicyConsts()
    naming_props = set([])

    mo_meta = MoMeta("OsARPLinkMonitoringPolicy", "osARPLinkMonitoringPolicy", "link-mon-pol", VersionMeta.Version302c, "InputOutput", 0x3fL, [], ["read-only"], [u'osEthBondIntf'], [u'osARPTarget'], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version302c, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "frequency": MoPropertyMeta("frequency", "frequency", "uint", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x8L, None, None, r"""[\-\.:_a-zA-Z0-9]{0,16}""", [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, 0x10L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x20L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "use_all_arp_targets": MoPropertyMeta("use_all_arp_targets", "useAllARPTargets", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, ["false", "no", "true", "yes"], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "frequency": "frequency", 
        "name": "name", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
        "useAllARPTargets": "use_all_arp_targets", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.frequency = None
        self.name = None
        self.sacl = None
        self.status = None
        self.use_all_arp_targets = None

        ManagedObject.__init__(self, "OsARPLinkMonitoringPolicy", parent_mo_or_dn, **kwargs)

