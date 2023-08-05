"""This module contains the general information for LstorageArrayAutoconfigPolicy ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class LstorageArrayAutoconfigPolicyConsts():
    INT_ID_NONE = "none"
    POLICY_OWNER_LOCAL = "local"
    POLICY_OWNER_PENDING_POLICY = "pending-policy"
    POLICY_OWNER_POLICY = "policy"


class LstorageArrayAutoconfigPolicy(ManagedObject):
    """This is LstorageArrayAutoconfigPolicy class."""

    consts = LstorageArrayAutoconfigPolicyConsts()
    naming_props = set([u'name'])

    mo_meta = MoMeta("LstorageArrayAutoconfigPolicy", "lstorageArrayAutoconfigPolicy", "storage-autoconfig-[name]", VersionMeta.Version302c, "InputOutput", 0x7ffL, [], ["admin", "ls-storage", "pn-policy"], [u'orgOrg'], [u'faultInst'], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version302c, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "descr": MoPropertyMeta("descr", "descr", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x4L, None, None, r"""[ !#$%&\(\)\*\+,\-\./:;\?@\[\]_\{\|\}~a-zA-Z0-9]{0,256}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, 0x8L, 0, 256, None, [], []), 
        "dst_dn": MoPropertyMeta("dst_dn", "dstDn", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x10L, 0, 256, None, [], []), 
        "int_id": MoPropertyMeta("int_id", "intId", "string", VersionMeta.Version302c, MoPropertyMeta.INTERNAL, None, None, None, None, ["none"], ["0-4294967295"]), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version302c, MoPropertyMeta.NAMING, 0x20L, None, None, r"""[\-\.:_a-zA-Z0-9]{1,16}""", [], []), 
        "oper_qualifier": MoPropertyMeta("oper_qualifier", "operQualifier", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, 0, 256, None, [], []), 
        "oper_src_templ_name": MoPropertyMeta("oper_src_templ_name", "operSrcTemplName", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, 0, 256, None, [], []), 
        "policy_level": MoPropertyMeta("policy_level", "policyLevel", "uint", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "policy_owner": MoPropertyMeta("policy_owner", "policyOwner", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x40L, None, None, None, ["local", "pending-policy", "policy"], []), 
        "prop_acl": MoPropertyMeta("prop_acl", "propAcl", "ulong", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "qualifier": MoPropertyMeta("qualifier", "qualifier", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x80L, None, None, r"""[\-\.:_a-zA-Z0-9]{0,16}""", [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, 0x100L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "src_templ_name": MoPropertyMeta("src_templ_name", "srcTemplName", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x200L, None, None, None, [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x400L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "descr": "descr", 
        "dn": "dn", 
        "dstDn": "dst_dn", 
        "intId": "int_id", 
        "name": "name", 
        "operQualifier": "oper_qualifier", 
        "operSrcTemplName": "oper_src_templ_name", 
        "policyLevel": "policy_level", 
        "policyOwner": "policy_owner", 
        "propAcl": "prop_acl", 
        "qualifier": "qualifier", 
        "rn": "rn", 
        "sacl": "sacl", 
        "srcTemplName": "src_templ_name", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, name, **kwargs):
        self._dirty_mask = 0
        self.name = name
        self.child_action = None
        self.descr = None
        self.dst_dn = None
        self.int_id = None
        self.oper_qualifier = None
        self.oper_src_templ_name = None
        self.policy_level = None
        self.policy_owner = None
        self.prop_acl = None
        self.qualifier = None
        self.sacl = None
        self.src_templ_name = None
        self.status = None

        ManagedObject.__init__(self, "LstorageArrayAutoconfigPolicy", parent_mo_or_dn, **kwargs)

