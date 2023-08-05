"""This module contains the general information for QosclassEthBE ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class QosclassEthBEConsts():
    ADMIN_STATE_DISABLED = "disabled"
    ADMIN_STATE_ENABLED = "enabled"
    BW_PERCENT_NOT_APPLICABLE = "not-applicable"
    COS_ANY = "any"
    DROP_DROP = "drop"
    DROP_NO_DROP = "no-drop"
    MTU_FC = "fc"
    MTU_NORMAL = "normal"
    MULTICAST_OPTIMIZE_FALSE = "false"
    MULTICAST_OPTIMIZE_NO = "no"
    MULTICAST_OPTIMIZE_TRUE = "true"
    MULTICAST_OPTIMIZE_YES = "yes"
    PRIORITY_BEST_EFFORT = "best-effort"
    PRIORITY_BRONZE = "bronze"
    PRIORITY_FC = "fc"
    PRIORITY_GOLD = "gold"
    PRIORITY_PLATINUM = "platinum"
    PRIORITY_SILVER = "silver"
    WEIGHT_BEST_EFFORT = "best-effort"
    WEIGHT_NONE = "none"


class QosclassEthBE(ManagedObject):
    """This is QosclassEthBE class."""

    consts = QosclassEthBEConsts()
    naming_props = set([])

    mo_meta = MoMeta("QosclassEthBE", "qosclassEthBE", "class-best-effort", VersionMeta.Version101e, "InputOutput", 0x1ffL, [], ["admin", "ext-lan-qos", "ext-san-qos", "ls-network", "ls-network-policy", "ls-qos-policy"], [u'qosclassDefinition'], [], ["Get", "Set"])

    prop_meta = {
        "admin_state": MoPropertyMeta("admin_state", "adminState", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["disabled", "enabled"], []), 
        "bw_percent": MoPropertyMeta("bw_percent", "bwPercent", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["not-applicable"], ["0-100"]), 
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version101e, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "cos": MoPropertyMeta("cos", "cos", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["any"], ["0-6", "255-255"]), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "drop": MoPropertyMeta("drop", "drop", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["drop", "no-drop"], []), 
        "mtu": MoPropertyMeta("mtu", "mtu", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x8L, None, None, None, ["fc", "normal"], ["0-4294967295"]), 
        "multicast_optimize": MoPropertyMeta("multicast_optimize", "multicastOptimize", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x10L, None, None, None, ["false", "no", "true", "yes"], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x20L, None, None, r"""[\-\.:_a-zA-Z0-9]{0,16}""", [], []), 
        "priority": MoPropertyMeta("priority", "priority", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["best-effort", "bronze", "fc", "gold", "platinum", "silver"], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x40L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x80L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "weight": MoPropertyMeta("weight", "weight", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x100L, None, None, None, ["best-effort", "none"], ["0-10"]), 
    }

    prop_map = {
        "adminState": "admin_state", 
        "bwPercent": "bw_percent", 
        "childAction": "child_action", 
        "cos": "cos", 
        "dn": "dn", 
        "drop": "drop", 
        "mtu": "mtu", 
        "multicastOptimize": "multicast_optimize", 
        "name": "name", 
        "priority": "priority", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
        "weight": "weight", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.admin_state = None
        self.bw_percent = None
        self.child_action = None
        self.cos = None
        self.drop = None
        self.mtu = None
        self.multicast_optimize = None
        self.name = None
        self.priority = None
        self.sacl = None
        self.status = None
        self.weight = None

        ManagedObject.__init__(self, "QosclassEthBE", parent_mo_or_dn, **kwargs)

