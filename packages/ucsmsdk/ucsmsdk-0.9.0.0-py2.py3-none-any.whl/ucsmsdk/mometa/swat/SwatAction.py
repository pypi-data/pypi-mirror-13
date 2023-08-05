"""This module contains the general information for SwatAction ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class SwatActionConsts():
    EVALUATION_METHOD_DETERMINISTIC = "Deterministic"
    EVALUATION_METHOD_RANDOM = "Random"
    INSTANCE_MOD_CREATE = "CREATE"
    INSTANCE_MOD_DELETE = "DELETE"
    TYPE_CRASH = "CRASH"
    TYPE_MOD = "MOD"
    TYPE_RETURN = "RETURN"
    TYPE_SLEEP = "SLEEP"


class SwatAction(ManagedObject):
    """This is SwatAction class."""

    consts = SwatActionConsts()
    naming_props = set([u'name'])

    mo_meta = MoMeta("SwatAction", "swatAction", "action-[name]", VersionMeta.Version101e, "InputOutput", 0xfffL, [], ["admin"], [u'swatInjection'], [u'swatCondition', u'swatTarget', u'swatTrigger'], ["Get"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version101e, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "evaluation_method": MoPropertyMeta("evaluation_method", "evaluationMethod", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x8L, None, None, None, ["Deterministic", "Random"], []), 
        "instance_mod": MoPropertyMeta("instance_mod", "instanceMod", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x10L, None, None, None, ["CREATE", "DELETE"], []), 
        "interval": MoPropertyMeta("interval", "interval", "uint", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x20L, None, None, None, [], []), 
        "max_hits": MoPropertyMeta("max_hits", "maxHits", "uint", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x40L, None, None, None, [], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x80L, None, None, r"""[\-\.:_a-zA-Z0-9]{1,16}""", [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x100L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "sleep_delay": MoPropertyMeta("sleep_delay", "sleepDelay", "uint", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x200L, None, None, None, [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x400L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "type": MoPropertyMeta("type", "type", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x800L, None, None, None, ["CRASH", "MOD", "RETURN", "SLEEP"], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "evaluationMethod": "evaluation_method", 
        "instanceMod": "instance_mod", 
        "interval": "interval", 
        "maxHits": "max_hits", 
        "name": "name", 
        "rn": "rn", 
        "sacl": "sacl", 
        "sleepDelay": "sleep_delay", 
        "status": "status", 
        "type": "type", 
    }

    def __init__(self, parent_mo_or_dn, name, **kwargs):
        self._dirty_mask = 0
        self.name = name
        self.child_action = None
        self.evaluation_method = None
        self.instance_mod = None
        self.interval = None
        self.max_hits = None
        self.sacl = None
        self.sleep_delay = None
        self.status = None
        self.type = None

        ManagedObject.__init__(self, "SwatAction", parent_mo_or_dn, **kwargs)

