"""This module contains the general information for MgmtHealthStatus ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class MgmtHealthStatusConsts():
    HEALTH_SEVERITY_CLEARED = "cleared"
    HEALTH_SEVERITY_CONDITION = "condition"
    HEALTH_SEVERITY_CRITICAL = "critical"
    HEALTH_SEVERITY_INFO = "info"
    HEALTH_SEVERITY_MAJOR = "major"
    HEALTH_SEVERITY_MINOR = "minor"
    HEALTH_SEVERITY_WARNING = "warning"


class MgmtHealthStatus(ManagedObject):
    """This is MgmtHealthStatus class."""

    consts = MgmtHealthStatusConsts()
    naming_props = set([])

    mo_meta = MoMeta("MgmtHealthStatus", "mgmtHealthStatus", "health", None, "InputOutput", 0x1fL, [], ["read-only"], [u'mgmtController', u'networkElement'], [u'faultInst', u'mgmtHealthAttr'], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", None, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", None, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "health_qualifier": MoPropertyMeta("health_qualifier", "healthQualifier", "string", None, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "health_severity": MoPropertyMeta("health_severity", "healthSeverity", "string", None, MoPropertyMeta.READ_ONLY, None, None, None, None, ["cleared", "condition", "critical", "info", "major", "minor", "warning"], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", None, MoPropertyMeta.READ_ONLY, 0x8L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", None, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", None, MoPropertyMeta.READ_WRITE, 0x10L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "healthQualifier": "health_qualifier", 
        "healthSeverity": "health_severity", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.health_qualifier = None
        self.health_severity = None
        self.sacl = None
        self.status = None

        ManagedObject.__init__(self, "MgmtHealthStatus", parent_mo_or_dn, **kwargs)

