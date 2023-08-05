"""This module contains the general information for StorageFlexFlashCard ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class StorageFlexFlashCardConsts():
    BLOCK_SIZE_UNKNOWN = "unknown"
    CARD_HEALTH_FF_PHY_HEALTH_NA = "FF_PHY_HEALTH_NA"
    CARD_HEALTH_FF_PHY_HEALTH_OK = "FF_PHY_HEALTH_OK"
    CARD_HEALTH_FF_PHY_UNHEALTHY_OTHER = "FF_PHY_UNHEALTHY_OTHER"
    CARD_HEALTH_FF_PHY_UNHEALTHY_RAID = "FF_PHY_UNHEALTHY_RAID"
    CARD_MODE_FF_PHY_DRIVE_PRIMARY = "FF_PHY_DRIVE_PRIMARY"
    CARD_MODE_FF_PHY_DRIVE_SECONDARY_ACT = "FF_PHY_DRIVE_SECONDARY_ACT"
    CARD_MODE_FF_PHY_DRIVE_SECONDARY_UNHEALTHY = "FF_PHY_DRIVE_SECONDARY_UNHEALTHY"
    CARD_MODE_FF_PHY_DRIVE_UNPAIRED_PRIMARY = "FF_PHY_DRIVE_UNPAIRED_PRIMARY"
    CARD_STATE_ACTIVE = "Active"
    CARD_STATE_CONFIGURED = "Configured"
    CARD_STATE_FAILED = "Failed"
    CARD_STATE_IGNORED = "Ignored"
    CARD_STATE_INITIALIZING = "Initializing"
    CARD_STATE_UNDEFINED = "Undefined"
    CARD_STATE_UNKNOWN = "Unknown"
    CARD_SYNC_AUTO = "Auto"
    CARD_SYNC_MANUAL = "Manual"
    CARD_SYNC_NA = "NA"
    CARD_SYNC_UNKNOWN = "Unknown"
    CONNECTION_PROTOCOL_NVME = "NVME"
    CONNECTION_PROTOCOL_SAS = "SAS"
    CONNECTION_PROTOCOL_SATA = "SATA"
    CONNECTION_PROTOCOL_UNSPECIFIED = "unspecified"
    NUMBER_OF_BLOCKS_UNKNOWN = "unknown"
    OPERABILITY_ACCESSIBILITY_PROBLEM = "accessibility-problem"
    OPERABILITY_AUTO_UPGRADE = "auto-upgrade"
    OPERABILITY_BIOS_POST_TIMEOUT = "bios-post-timeout"
    OPERABILITY_CHASSIS_LIMIT_EXCEEDED = "chassis-limit-exceeded"
    OPERABILITY_CONFIG = "config"
    OPERABILITY_DECOMISSIONING = "decomissioning"
    OPERABILITY_DEGRADED = "degraded"
    OPERABILITY_DISABLED = "disabled"
    OPERABILITY_DISCOVERY = "discovery"
    OPERABILITY_DISCOVERY_FAILED = "discovery-failed"
    OPERABILITY_EQUIPMENT_PROBLEM = "equipment-problem"
    OPERABILITY_FABRIC_CONN_PROBLEM = "fabric-conn-problem"
    OPERABILITY_FABRIC_UNSUPPORTED_CONN = "fabric-unsupported-conn"
    OPERABILITY_IDENTIFY = "identify"
    OPERABILITY_IDENTITY_UNESTABLISHABLE = "identity-unestablishable"
    OPERABILITY_INOPERABLE = "inoperable"
    OPERABILITY_LINK_ACTIVATE_BLOCKED = "link-activate-blocked"
    OPERABILITY_MALFORMED_FRU = "malformed-fru"
    OPERABILITY_NOT_SUPPORTED = "not-supported"
    OPERABILITY_OPERABLE = "operable"
    OPERABILITY_PEER_COMM_PROBLEM = "peer-comm-problem"
    OPERABILITY_PERFORMANCE_PROBLEM = "performance-problem"
    OPERABILITY_POST_FAILURE = "post-failure"
    OPERABILITY_POWER_PROBLEM = "power-problem"
    OPERABILITY_POWERED_OFF = "powered-off"
    OPERABILITY_REMOVED = "removed"
    OPERABILITY_THERMAL_PROBLEM = "thermal-problem"
    OPERABILITY_UNKNOWN = "unknown"
    OPERABILITY_UPGRADE_PROBLEM = "upgrade-problem"
    OPERABILITY_VOLTAGE_PROBLEM = "voltage-problem"
    PRESENCE_EMPTY = "empty"
    PRESENCE_EQUIPPED = "equipped"
    PRESENCE_EQUIPPED_DEPRECATED = "equipped-deprecated"
    PRESENCE_EQUIPPED_IDENTITY_UNESTABLISHABLE = "equipped-identity-unestablishable"
    PRESENCE_EQUIPPED_NOT_PRIMARY = "equipped-not-primary"
    PRESENCE_EQUIPPED_SLAVE = "equipped-slave"
    PRESENCE_EQUIPPED_UNSUPPORTED = "equipped-unsupported"
    PRESENCE_EQUIPPED_WITH_MALFORMED_FRU = "equipped-with-malformed-fru"
    PRESENCE_INACCESSIBLE = "inaccessible"
    PRESENCE_MISMATCH = "mismatch"
    PRESENCE_MISMATCH_IDENTITY_UNESTABLISHABLE = "mismatch-identity-unestablishable"
    PRESENCE_MISMATCH_SLAVE = "mismatch-slave"
    PRESENCE_MISSING = "missing"
    PRESENCE_MISSING_SLAVE = "missing-slave"
    PRESENCE_NOT_SUPPORTED = "not-supported"
    PRESENCE_UNAUTHORIZED = "unauthorized"
    PRESENCE_UNKNOWN = "unknown"
    WRITE_ENABLE_NO = "no"
    WRITE_ENABLE_YES = "yes"


class StorageFlexFlashCard(ManagedObject):
    """This is StorageFlexFlashCard class."""

    consts = StorageFlexFlashCardConsts()
    naming_props = set([u'slotNumber'])

    mo_meta = MoMeta("StorageFlexFlashCard", "storageFlexFlashCard", "card-[slot_number]", VersionMeta.Version221b, "InputOutput", 0x7fL, [], ["read-only"], [u'storageFlexFlashController'], [u'faultInst', u'storageFlexFlashDrive'], ["Get"])

    prop_meta = {
        "block_size": MoPropertyMeta("block_size", "blockSize", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["unknown"], ["0-4294967295"]), 
        "card_health": MoPropertyMeta("card_health", "cardHealth", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["FF_PHY_HEALTH_NA", "FF_PHY_HEALTH_OK", "FF_PHY_UNHEALTHY_OTHER", "FF_PHY_UNHEALTHY_RAID"], []), 
        "card_mode": MoPropertyMeta("card_mode", "cardMode", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["FF_PHY_DRIVE_PRIMARY", "FF_PHY_DRIVE_SECONDARY_ACT", "FF_PHY_DRIVE_SECONDARY_UNHEALTHY", "FF_PHY_DRIVE_UNPAIRED_PRIMARY"], []), 
        "card_state": MoPropertyMeta("card_state", "cardState", "string", VersionMeta.Version223a, MoPropertyMeta.READ_ONLY, None, None, None, None, ["Active", "Configured", "Failed", "Ignored", "Initializing", "Undefined", "Unknown"], []), 
        "card_sync": MoPropertyMeta("card_sync", "cardSync", "string", VersionMeta.Version223a, MoPropertyMeta.READ_ONLY, None, None, None, None, ["Auto", "Manual", "NA", "Unknown"], []), 
        "card_type": MoPropertyMeta("card_type", "cardType", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version221b, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "connection_protocol": MoPropertyMeta("connection_protocol", "connectionProtocol", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["NVME", "SAS", "SATA", "unspecified"], []), 
        "controller_index": MoPropertyMeta("controller_index", "controllerIndex", "ushort", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "drives_enabled": MoPropertyMeta("drives_enabled", "drivesEnabled", "string", VersionMeta.Version223a, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "id": MoPropertyMeta("id", "id", "uint", VersionMeta.Version221b, MoPropertyMeta.READ_WRITE, 0x8L, None, None, None, [], []), 
        "mfg_date": MoPropertyMeta("mfg_date", "mfgDate", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "mfg_id": MoPropertyMeta("mfg_id", "mfgId", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "model": MoPropertyMeta("model", "model", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "number_of_blocks": MoPropertyMeta("number_of_blocks", "numberOfBlocks", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["unknown"], ["0-4294967295"]), 
        "oem_id": MoPropertyMeta("oem_id", "oemId", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "oper_qualifier_reason": MoPropertyMeta("oper_qualifier_reason", "operQualifierReason", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, r"""[ !#$%&\(\)\*\+,\-\./:;\?@\[\]_\{\|\}~a-zA-Z0-9]{0,256}""", [], []), 
        "operability": MoPropertyMeta("operability", "operability", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["accessibility-problem", "auto-upgrade", "bios-post-timeout", "chassis-limit-exceeded", "config", "decomissioning", "degraded", "disabled", "discovery", "discovery-failed", "equipment-problem", "fabric-conn-problem", "fabric-unsupported-conn", "identify", "identity-unestablishable", "inoperable", "link-activate-blocked", "malformed-fru", "not-supported", "operable", "peer-comm-problem", "performance-problem", "post-failure", "power-problem", "powered-off", "removed", "thermal-problem", "unknown", "upgrade-problem", "voltage-problem"], []), 
        "partition_count": MoPropertyMeta("partition_count", "partitionCount", "ushort", VersionMeta.Version223a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "presence": MoPropertyMeta("presence", "presence", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["empty", "equipped", "equipped-deprecated", "equipped-identity-unestablishable", "equipped-not-primary", "equipped-slave", "equipped-unsupported", "equipped-with-malformed-fru", "inaccessible", "mismatch", "mismatch-identity-unestablishable", "mismatch-slave", "missing", "missing-slave", "not-supported", "unauthorized", "unknown"], []), 
        "read_error_threshold": MoPropertyMeta("read_error_threshold", "readErrorThreshold", "uint", VersionMeta.Version223a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "read_io_error_count": MoPropertyMeta("read_io_error_count", "readIOErrorCount", "uint", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "revision": MoPropertyMeta("revision", "revision", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, 0x10L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "serial": MoPropertyMeta("serial", "serial", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "signature": MoPropertyMeta("signature", "signature", "string", VersionMeta.Version223a, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "size": MoPropertyMeta("size", "size", "ulong", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "slot_number": MoPropertyMeta("slot_number", "slotNumber", "ushort", VersionMeta.Version221b, MoPropertyMeta.NAMING, 0x20L, None, None, None, [], ["1-64"]), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version221b, MoPropertyMeta.READ_WRITE, 0x40L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "vendor": MoPropertyMeta("vendor", "vendor", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "write_enable": MoPropertyMeta("write_enable", "writeEnable", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, ["no", "yes"], []), 
        "write_error_threshold": MoPropertyMeta("write_error_threshold", "writeErrorThreshold", "uint", VersionMeta.Version223a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "write_io_error_count": MoPropertyMeta("write_io_error_count", "writeIOErrorCount", "uint", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
    }

    prop_map = {
        "blockSize": "block_size", 
        "cardHealth": "card_health", 
        "cardMode": "card_mode", 
        "cardState": "card_state", 
        "cardSync": "card_sync", 
        "cardType": "card_type", 
        "childAction": "child_action", 
        "connectionProtocol": "connection_protocol", 
        "controllerIndex": "controller_index", 
        "dn": "dn", 
        "drivesEnabled": "drives_enabled", 
        "id": "id", 
        "mfgDate": "mfg_date", 
        "mfgId": "mfg_id", 
        "model": "model", 
        "numberOfBlocks": "number_of_blocks", 
        "oemId": "oem_id", 
        "operQualifierReason": "oper_qualifier_reason", 
        "operability": "operability", 
        "partitionCount": "partition_count", 
        "presence": "presence", 
        "readErrorThreshold": "read_error_threshold", 
        "readIOErrorCount": "read_io_error_count", 
        "revision": "revision", 
        "rn": "rn", 
        "sacl": "sacl", 
        "serial": "serial", 
        "signature": "signature", 
        "size": "size", 
        "slotNumber": "slot_number", 
        "status": "status", 
        "vendor": "vendor", 
        "writeEnable": "write_enable", 
        "writeErrorThreshold": "write_error_threshold", 
        "writeIOErrorCount": "write_io_error_count", 
    }

    def __init__(self, parent_mo_or_dn, slot_number, **kwargs):
        self._dirty_mask = 0
        self.slot_number = slot_number
        self.block_size = None
        self.card_health = None
        self.card_mode = None
        self.card_state = None
        self.card_sync = None
        self.card_type = None
        self.child_action = None
        self.connection_protocol = None
        self.controller_index = None
        self.drives_enabled = None
        self.id = None
        self.mfg_date = None
        self.mfg_id = None
        self.model = None
        self.number_of_blocks = None
        self.oem_id = None
        self.oper_qualifier_reason = None
        self.operability = None
        self.partition_count = None
        self.presence = None
        self.read_error_threshold = None
        self.read_io_error_count = None
        self.revision = None
        self.sacl = None
        self.serial = None
        self.signature = None
        self.size = None
        self.status = None
        self.vendor = None
        self.write_enable = None
        self.write_error_threshold = None
        self.write_io_error_count = None

        ManagedObject.__init__(self, "StorageFlexFlashCard", parent_mo_or_dn, **kwargs)

