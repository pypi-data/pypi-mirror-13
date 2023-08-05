"""This module contains the general information for StorageVirtualDriveRef ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class StorageVirtualDriveRefConsts():
    ADMIN_STATE_OFFLINE = "offline"
    ADMIN_STATE_ONLINE = "online"
    ADMIN_STATE_UNDEPLOYED = "undeployed"
    CONFIG_STATE_APPLIED = "applied"
    CONFIG_STATE_APPLY_FAILED = "apply-failed"
    CONFIG_STATE_APPLYING = "applying"
    CONFIG_STATE_NOT_APPLIED = "not-applied"
    CONFIG_STATE_NOT_IN_USE = "not-in-use"
    CONFIG_STATE_ORPHANED = "orphaned"
    IS_BOOTABLE_DISABLED = "disabled"
    IS_BOOTABLE_ENABLED = "enabled"
    ORDER_LOWEST_AVAILABLE = "lowest-available"
    ORDER_NOT_APPLICABLE = "not-applicable"
    RAID_LEVEL_MIRROR = "mirror"
    RAID_LEVEL_MIRROR_STRIPE = "mirror-stripe"
    RAID_LEVEL_RAID = "raid"
    RAID_LEVEL_SIMPLE = "simple"
    RAID_LEVEL_STRIPE = "stripe"
    RAID_LEVEL_STRIPE_DUAL_PARITY = "stripe-dual-parity"
    RAID_LEVEL_STRIPE_DUAL_PARITY_STRIPE = "stripe-dual-parity-stripe"
    RAID_LEVEL_STRIPE_PARITY = "stripe-parity"
    RAID_LEVEL_STRIPE_PARITY_STRIPE = "stripe-parity-stripe"
    RAID_LEVEL_UNSPECIFIED = "unspecified"


class StorageVirtualDriveRef(ManagedObject):
    """This is StorageVirtualDriveRef class."""

    consts = StorageVirtualDriveRefConsts()
    naming_props = set([u'lunItemName'])

    mo_meta = MoMeta("StorageVirtualDriveRef", "storageVirtualDriveRef", "vdrive-ref-[lun_item_name]", VersionMeta.Version224b, "InputOutput", 0x3ffL, [], ["admin", "ls-compute", "ls-config", "ls-server", "ls-storage"], [u'lsServer'], [u'lstorageDiskGroupConfigDef', u'storageLunResourceSelectionLog'], ["Get"])

    prop_meta = {
        "admin_name": MoPropertyMeta("admin_name", "adminName", "string", VersionMeta.Version224b, MoPropertyMeta.READ_WRITE, 0x2L, None, None, r"""[\-\.:_a-zA-Z0-9]{0,16}""", [], []), 
        "admin_state": MoPropertyMeta("admin_state", "adminState", "string", VersionMeta.Version224b, MoPropertyMeta.READ_WRITE, 0x4L, None, None, None, ["offline", "online", "undeployed"], []), 
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version224b, MoPropertyMeta.INTERNAL, 0x8L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "config_state": MoPropertyMeta("config_state", "configState", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["applied", "apply-failed", "applying", "not-applied", "not-in-use", "orphaned"], []), 
        "disk_selection_order": MoPropertyMeta("disk_selection_order", "diskSelectionOrder", "ushort", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "disk_selection_ts": MoPropertyMeta("disk_selection_ts", "diskSelectionTs", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, None, None, r"""([0-9]){4}-([0-9]){2}-([0-9]){2}T([0-9]){2}:([0-9]){2}:([0-9]){2}((\.([0-9]){3})){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, 0x10L, 0, 256, None, [], []), 
        "is_bootable": MoPropertyMeta("is_bootable", "isBootable", "string", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, ["disabled", "enabled"], []), 
        "lun_dn": MoPropertyMeta("lun_dn", "lunDn", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, 0, 256, None, [], []), 
        "lun_item_dn": MoPropertyMeta("lun_item_dn", "lunItemDn", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, 0, 256, None, [], []), 
        "lun_item_name": MoPropertyMeta("lun_item_name", "lunItemName", "string", VersionMeta.Version224b, MoPropertyMeta.NAMING, 0x20L, 1, 32, r"""[\-\.:_a-zA-Z0-9]{1,16}""", [], []), 
        "lun_name": MoPropertyMeta("lun_name", "lunName", "string", VersionMeta.Version224b, MoPropertyMeta.READ_WRITE, 0x40L, 0, 31, r"""[\-\.:_a-zA-Z0-9]{0,15}""", [], []), 
        "order": MoPropertyMeta("order", "order", "string", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, ["lowest-available", "not-applicable"], ["0-64", "1-64"]), 
        "raid_level": MoPropertyMeta("raid_level", "raidLevel", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["mirror", "mirror-stripe", "raid", "simple", "stripe", "stripe-dual-parity", "stripe-dual-parity-stripe", "stripe-parity", "stripe-parity-stripe", "unspecified"], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, 0x80L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "size": MoPropertyMeta("size", "size", "ulong", VersionMeta.Version224b, MoPropertyMeta.READ_WRITE, 0x100L, None, None, None, [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version224b, MoPropertyMeta.READ_WRITE, 0x200L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "uuid": MoPropertyMeta("uuid", "uuid", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, None, None, r"""(([0-9a-fA-F]){8}\-([0-9a-fA-F]){4}\-([0-9a-fA-F]){4}\-([0-9a-fA-F]){4}\-([0-9a-fA-F]){12})|0""", [], []), 
        "vendor_uuid": MoPropertyMeta("vendor_uuid", "vendorUuid", "string", VersionMeta.Version224b, MoPropertyMeta.READ_ONLY, None, None, None, r"""(([0-9a-fA-F]){8}\-([0-9a-fA-F]){4}\-([0-9a-fA-F]){4}\-([0-9a-fA-F]){4}\-([0-9a-fA-F]){12})|0""", [], []), 
    }

    prop_map = {
        "adminName": "admin_name", 
        "adminState": "admin_state", 
        "childAction": "child_action", 
        "configState": "config_state", 
        "diskSelectionOrder": "disk_selection_order", 
        "diskSelectionTs": "disk_selection_ts", 
        "dn": "dn", 
        "isBootable": "is_bootable", 
        "lunDn": "lun_dn", 
        "lunItemDn": "lun_item_dn", 
        "lunItemName": "lun_item_name", 
        "lunName": "lun_name", 
        "order": "order", 
        "raidLevel": "raid_level", 
        "rn": "rn", 
        "sacl": "sacl", 
        "size": "size", 
        "status": "status", 
        "uuid": "uuid", 
        "vendorUuid": "vendor_uuid", 
    }

    def __init__(self, parent_mo_or_dn, lun_item_name, **kwargs):
        self._dirty_mask = 0
        self.lun_item_name = lun_item_name
        self.admin_name = None
        self.admin_state = None
        self.child_action = None
        self.config_state = None
        self.disk_selection_order = None
        self.disk_selection_ts = None
        self.is_bootable = None
        self.lun_dn = None
        self.lun_item_dn = None
        self.lun_name = None
        self.order = None
        self.raid_level = None
        self.sacl = None
        self.size = None
        self.status = None
        self.uuid = None
        self.vendor_uuid = None

        ManagedObject.__init__(self, "StorageVirtualDriveRef", parent_mo_or_dn, **kwargs)

