"""This module contains the general information for EquipmentBladeBiosCapProvider ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class EquipmentBladeBiosCapProviderConsts():
    DELETED_FALSE = "false"
    DELETED_NO = "no"
    DELETED_TRUE = "true"
    DELETED_YES = "yes"
    DEPRECATED_FALSE = "false"
    DEPRECATED_NO = "no"
    DEPRECATED_TRUE = "true"
    DEPRECATED_YES = "yes"


class EquipmentBladeBiosCapProvider(ManagedObject):
    """This is EquipmentBladeBiosCapProvider class."""

    consts = EquipmentBladeBiosCapProviderConsts()
    naming_props = set([u'vendor', u'model', u'revision'])

    mo_meta = MoMeta("EquipmentBladeBiosCapProvider", "equipmentBladeBiosCapProvider", "manufacturer-[vendor]-model-[model]-revision-[revision]", VersionMeta.Version101e, "InputOutput", 0x1ffL, [], [""], [u'capabilityCatalogue'], [u'biosRef', u'equipmentManufacturingDef', u'equipmentPhysicalDef', u'equipmentPicture', u'equipmentServiceDef', u'equipmentSlotArrayRef', u'firmwareType', u'firmwareUpgradeConstraint'], ["Get"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version101e, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "deleted": MoPropertyMeta("deleted", "deleted", "string", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, None, None, None, None, ["false", "no", "true", "yes"], []), 
        "deprecated": MoPropertyMeta("deprecated", "deprecated", "string", VersionMeta.Version131c, MoPropertyMeta.READ_ONLY, None, None, None, None, ["false", "no", "true", "yes"], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "element_load_failures": MoPropertyMeta("element_load_failures", "elementLoadFailures", "uint", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "elements_loaded": MoPropertyMeta("elements_loaded", "elementsLoaded", "uint", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "gencount": MoPropertyMeta("gencount", "gencount", "uint", VersionMeta.Version131c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "load_errors": MoPropertyMeta("load_errors", "loadErrors", "uint", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "load_warnings": MoPropertyMeta("load_warnings", "loadWarnings", "uint", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "mgmt_plane_ver": MoPropertyMeta("mgmt_plane_ver", "mgmtPlaneVer", "string", VersionMeta.Version131c, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "model": MoPropertyMeta("model", "model", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x8L, 1, 510, None, [], []), 
        "product_name": MoPropertyMeta("product_name", "productName", "string", VersionMeta.Version131c, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "prom_card_type": MoPropertyMeta("prom_card_type", "promCardType", "ushort", VersionMeta.Version141i, MoPropertyMeta.READ_WRITE, 0x10L, None, None, None, [], []), 
        "revision": MoPropertyMeta("revision", "revision", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x20L, 1, 510, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x40L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x80L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "vendor": MoPropertyMeta("vendor", "vendor", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x100L, 1, 510, None, [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "deleted": "deleted", 
        "deprecated": "deprecated", 
        "dn": "dn", 
        "elementLoadFailures": "element_load_failures", 
        "elementsLoaded": "elements_loaded", 
        "gencount": "gencount", 
        "loadErrors": "load_errors", 
        "loadWarnings": "load_warnings", 
        "mgmtPlaneVer": "mgmt_plane_ver", 
        "model": "model", 
        "productName": "product_name", 
        "promCardType": "prom_card_type", 
        "revision": "revision", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
        "vendor": "vendor", 
    }

    def __init__(self, parent_mo_or_dn, vendor, model, revision, **kwargs):
        self._dirty_mask = 0
        self.vendor = vendor
        self.model = model
        self.revision = revision
        self.child_action = None
        self.deleted = None
        self.deprecated = None
        self.element_load_failures = None
        self.elements_loaded = None
        self.gencount = None
        self.load_errors = None
        self.load_warnings = None
        self.mgmt_plane_ver = None
        self.product_name = None
        self.prom_card_type = None
        self.sacl = None
        self.status = None

        ManagedObject.__init__(self, "EquipmentBladeBiosCapProvider", parent_mo_or_dn, **kwargs)

