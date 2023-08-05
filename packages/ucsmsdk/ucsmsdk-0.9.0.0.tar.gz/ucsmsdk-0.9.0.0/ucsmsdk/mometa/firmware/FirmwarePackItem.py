"""This module contains the general information for FirmwarePackItem ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class FirmwarePackItemConsts():
    PRESENCE_MISSING = "missing"
    PRESENCE_PRESENT = "present"
    PRESENCE_UNKNOWN = "unknown"
    TYPE_ADAPTOR = "adaptor"
    TYPE_BLADE_BIOS = "blade-bios"
    TYPE_BLADE_CONTROLLER = "blade-controller"
    TYPE_BOARD_CONTROLLER = "board-controller"
    TYPE_FLEXFLASH_CONTROLLER = "flexflash-controller"
    TYPE_GRAPHICS_CARD = "graphics-card"
    TYPE_HOST_HBA = "host-hba"
    TYPE_HOST_HBA_OPTIONROM = "host-hba-optionrom"
    TYPE_HOST_NIC = "host-nic"
    TYPE_HOST_NIC_OPTIONROM = "host-nic-optionrom"
    TYPE_IOCARD = "iocard"
    TYPE_LOCAL_DISK = "local-disk"
    TYPE_PSU = "psu"
    TYPE_SAS_EXPANDER = "sas-expander"
    TYPE_STORAGE_CONTROLLER = "storage-controller"
    TYPE_STORAGE_DEV_BRIDGE = "storage-dev-bridge"
    TYPE_STORAGE_NODE_CONTROLLER = "storage-node-controller"
    TYPE_SWITCH_KERNEL = "switch-kernel"
    TYPE_SWITCH_SOFTWARE = "switch-software"
    TYPE_SYSTEM = "system"
    TYPE_UNSPECIFIED = "unspecified"


class FirmwarePackItem(ManagedObject):
    """This is FirmwarePackItem class."""

    consts = FirmwarePackItemConsts()
    naming_props = set([u'hwVendor', u'hwModel', u'type'])

    mo_meta = MoMeta("FirmwarePackItem", "firmwarePackItem", "pack-image-[hw_vendor]|[hw_model]|[type]", VersionMeta.Version101e, "InputOutput", 0x1ffL, [], ["admin"], [u'firmwareCatalogPack', u'firmwareComputeHostPack', u'firmwareComputeMgmtPack', u'firmwareComputeStoragePack', u'firmwareInfraPack'], [u'faultInst'], ["Add", "Get", "Remove", "Set"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version101e, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "hw_model": MoPropertyMeta("hw_model", "hwModel", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x8L, 1, 510, None, [], []), 
        "hw_vendor": MoPropertyMeta("hw_vendor", "hwVendor", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x10L, 1, 510, None, [], []), 
        "presence": MoPropertyMeta("presence", "presence", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["missing", "present", "unknown"], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x20L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x40L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "type": MoPropertyMeta("type", "type", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x80L, None, None, None, ["adaptor", "blade-bios", "blade-controller", "board-controller", "flexflash-controller", "graphics-card", "host-hba", "host-hba-optionrom", "host-nic", "host-nic-optionrom", "iocard", "local-disk", "psu", "sas-expander", "storage-controller", "storage-dev-bridge", "storage-node-controller", "switch-kernel", "switch-software", "system", "unspecified"], []), 
        "version": MoPropertyMeta("version", "version", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x100L, 0, 510, None, [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "hwModel": "hw_model", 
        "hwVendor": "hw_vendor", 
        "presence": "presence", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
        "type": "type", 
        "version": "version", 
    }

    def __init__(self, parent_mo_or_dn, hw_vendor, hw_model, type, **kwargs):
        self._dirty_mask = 0
        self.hw_vendor = hw_vendor
        self.hw_model = hw_model
        self.type = type
        self.child_action = None
        self.presence = None
        self.sacl = None
        self.status = None
        self.version = None

        ManagedObject.__init__(self, "FirmwarePackItem", parent_mo_or_dn, **kwargs)

