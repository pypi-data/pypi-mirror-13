"""This module contains the general information for FabricSwChPhEp ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class FabricSwChPhEpConsts():
    ADMIN_STATE_DISABLED = "disabled"
    ADMIN_STATE_ENABLED = "enabled"
    ADMIN_STATE_REMOVE = "remove"
    AUTO_NEGOTIATE_FALSE = "false"
    AUTO_NEGOTIATE_NO = "no"
    AUTO_NEGOTIATE_TRUE = "true"
    AUTO_NEGOTIATE_YES = "yes"
    CHASSIS_ID_N_A = "N/A"
    CONFIG_QUALIFIER_NOT_APPLICABLE = "not-applicable"
    CONFIG_QUALIFIER_UNCLEAN_CONFIGURATION = "unclean-configuration"
    EQ_TYPE_BLADE = "blade"
    EQ_TYPE_CARTRIDGE = "cartridge"
    EQ_TYPE_CHASSIS = "chassis"
    EQ_TYPE_FEX = "fex"
    EQ_TYPE_RACK_UNIT = "rack-unit"
    EQ_TYPE_SERVER_UNIT = "server-unit"
    EQ_TYPE_UNKNOWN = "unknown"
    IF_ROLE_DIAG = "diag"
    IF_ROLE_FCOE_NAS_STORAGE = "fcoe-nas-storage"
    IF_ROLE_FCOE_STORAGE = "fcoe-storage"
    IF_ROLE_FCOE_UPLINK = "fcoe-uplink"
    IF_ROLE_MGMT = "mgmt"
    IF_ROLE_MONITOR = "monitor"
    IF_ROLE_NAS_STORAGE = "nas-storage"
    IF_ROLE_NETWORK = "network"
    IF_ROLE_NETWORK_FCOE_UPLINK = "network-fcoe-uplink"
    IF_ROLE_SERVER = "server"
    IF_ROLE_SERVICE = "service"
    IF_ROLE_STORAGE = "storage"
    IF_ROLE_UNKNOWN = "unknown"
    IF_TYPE_AGGREGATION = "aggregation"
    IF_TYPE_PHYSICAL = "physical"
    IF_TYPE_UNKNOWN = "unknown"
    IF_TYPE_VIRTUAL = "virtual"
    LC_IN_SERVICE = "in-service"
    LC_OUT_OF_SERVICE = "out-of-service"
    LC_OUT_OF_SERVICE_SLAVE = "out-of-service-slave"
    LIC_STATE_LICENSE_EXPIRED = "license-expired"
    LIC_STATE_LICENSE_GRACEPERIOD = "license-graceperiod"
    LIC_STATE_LICENSE_INSUFFICIENT = "license-insufficient"
    LIC_STATE_LICENSE_OK = "license-ok"
    LIC_STATE_NOT_APPLICABLE = "not-applicable"
    LIC_STATE_UNKNOWN = "unknown"
    OPER_STATE_DOWN = "down"
    OPER_STATE_ERROR_MISCONFIGURED = "error-misconfigured"
    OPER_STATE_ERROR_UNSUPPORTED_MINI_SERVER_PORT = "error-unsupported-mini-server-port"
    OPER_STATE_FAILED = "failed"
    OPER_STATE_UNKNOWN = "unknown"
    OPER_STATE_UP = "up"
    PEER_CHASSIS_ID_N_A = "N/A"
    SWITCH_ID_A = "A"
    SWITCH_ID_B = "B"
    SWITCH_ID_NONE = "NONE"


class FabricSwChPhEp(ManagedObject):
    """This is FabricSwChPhEp class."""

    consts = FabricSwChPhEpConsts()
    naming_props = set([u'vendor', u'model', u'serial'])

    mo_meta = MoMeta("FabricSwChPhEp", "fabricSwChPhEp", "chassis-ep-ven-[vendor]-mod[model]-ser-[serial]", VersionMeta.Version101e, "InputOutput", 0xfffL, [], ["admin", "pn-equipment", "pn-maintenance", "pn-policy"], [u'fabricDceSrv'], [u'faultInst'], ["Get", "Set"])

    prop_meta = {
        "admin_state": MoPropertyMeta("admin_state", "adminState", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x2L, None, None, None, ["disabled", "enabled", "remove"], []), 
        "aggr_port_id": MoPropertyMeta("aggr_port_id", "aggrPortId", "uint", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "auto_negotiate": MoPropertyMeta("auto_negotiate", "autoNegotiate", "string", None, MoPropertyMeta.READ_WRITE, 0x4L, None, None, None, ["false", "no", "true", "yes"], []), 
        "chassis_id": MoPropertyMeta("chassis_id", "chassisId", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x8L, None, None, None, ["N/A"], ["1-40"]), 
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version101e, MoPropertyMeta.INTERNAL, 0x10L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "config_qualifier": MoPropertyMeta("config_qualifier", "configQualifier", "string", None, MoPropertyMeta.READ_ONLY, None, None, None, None, ["not-applicable", "unclean-configuration"], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x20L, 0, 256, None, [], []), 
        "ep_dn": MoPropertyMeta("ep_dn", "epDn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, 0, 256, None, [], []), 
        "eq_type": MoPropertyMeta("eq_type", "eqType", "string", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, None, None, None, None, ["blade", "cartridge", "chassis", "fex", "rack-unit", "server-unit", "unknown"], []), 
        "flt_aggr": MoPropertyMeta("flt_aggr", "fltAggr", "ulong", VersionMeta.Version201m, MoPropertyMeta.INTERNAL, None, None, None, None, [], []), 
        "if_role": MoPropertyMeta("if_role", "ifRole", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["diag", "fcoe-nas-storage", "fcoe-storage", "fcoe-uplink", "mgmt", "monitor", "nas-storage", "network", "network-fcoe-uplink", "server", "service", "storage", "unknown"], []), 
        "if_type": MoPropertyMeta("if_type", "ifType", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["aggregation", "physical", "unknown", "virtual"], []), 
        "lc": MoPropertyMeta("lc", "lc", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["in-service", "out-of-service", "out-of-service-slave"], []), 
        "lic_gp": MoPropertyMeta("lic_gp", "licGP", "ulong", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "lic_state": MoPropertyMeta("lic_state", "licState", "string", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, None, None, None, None, ["license-expired", "license-graceperiod", "license-insufficient", "license-ok", "not-applicable", "unknown"], []), 
        "locale": MoPropertyMeta("locale", "locale", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|unknown|server|chassis|internal|external),){0,5}(defaultValue|unknown|server|chassis|internal|external){0,1}""", [], []), 
        "model": MoPropertyMeta("model", "model", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x40L, 1, 510, None, [], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x80L, None, None, r"""[\-\.:_a-zA-Z0-9]{0,16}""", [], []), 
        "oper_state": MoPropertyMeta("oper_state", "operState", "string", VersionMeta.Version201m, MoPropertyMeta.READ_ONLY, None, None, None, None, ["down", "error-misconfigured", "error-unsupported-mini-server-port", "failed", "unknown", "up"], []), 
        "oper_state_reason": MoPropertyMeta("oper_state_reason", "operStateReason", "string", VersionMeta.Version201m, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "peer_aggr_port_id": MoPropertyMeta("peer_aggr_port_id", "peerAggrPortId", "uint", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "peer_chassis_id": MoPropertyMeta("peer_chassis_id", "peerChassisId", "string", VersionMeta.Version141i, MoPropertyMeta.READ_ONLY, None, None, None, None, ["N/A"], ["0-255"]), 
        "peer_dn": MoPropertyMeta("peer_dn", "peerDn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, 0, 256, None, [], []), 
        "peer_port_id": MoPropertyMeta("peer_port_id", "peerPortId", "uint", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "peer_slot_id": MoPropertyMeta("peer_slot_id", "peerSlotId", "uint", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "port_id": MoPropertyMeta("port_id", "portId", "uint", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, [], ["1-48"]), 
        "revision": MoPropertyMeta("revision", "revision", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, 0, 510, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, 0x100L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "serial": MoPropertyMeta("serial", "serial", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x200L, 1, 510, None, [], []), 
        "slot_id": MoPropertyMeta("slot_id", "slotId", "uint", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, [], ["1-4"]), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version101e, MoPropertyMeta.READ_WRITE, 0x400L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "switch_id": MoPropertyMeta("switch_id", "switchId", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, None, ["A", "B", "NONE"], []), 
        "transport": MoPropertyMeta("transport", "transport", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|unknown|ether|dce|fc),){0,4}(defaultValue|unknown|ether|dce|fc){0,1}""", [], []), 
        "type": MoPropertyMeta("type", "type", "string", VersionMeta.Version101e, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|unknown|lan|san|ipc),){0,4}(defaultValue|unknown|lan|san|ipc){0,1}""", [], []), 
        "vendor": MoPropertyMeta("vendor", "vendor", "string", VersionMeta.Version101e, MoPropertyMeta.NAMING, 0x800L, 1, 510, None, [], []), 
    }

    prop_map = {
        "adminState": "admin_state", 
        "aggrPortId": "aggr_port_id", 
        "autoNegotiate": "auto_negotiate", 
        "chassisId": "chassis_id", 
        "childAction": "child_action", 
        "configQualifier": "config_qualifier", 
        "dn": "dn", 
        "epDn": "ep_dn", 
        "eqType": "eq_type", 
        "fltAggr": "flt_aggr", 
        "ifRole": "if_role", 
        "ifType": "if_type", 
        "lc": "lc", 
        "licGP": "lic_gp", 
        "licState": "lic_state", 
        "locale": "locale", 
        "model": "model", 
        "name": "name", 
        "operState": "oper_state", 
        "operStateReason": "oper_state_reason", 
        "peerAggrPortId": "peer_aggr_port_id", 
        "peerChassisId": "peer_chassis_id", 
        "peerDn": "peer_dn", 
        "peerPortId": "peer_port_id", 
        "peerSlotId": "peer_slot_id", 
        "portId": "port_id", 
        "revision": "revision", 
        "rn": "rn", 
        "sacl": "sacl", 
        "serial": "serial", 
        "slotId": "slot_id", 
        "status": "status", 
        "switchId": "switch_id", 
        "transport": "transport", 
        "type": "type", 
        "vendor": "vendor", 
    }

    def __init__(self, parent_mo_or_dn, vendor, model, serial, **kwargs):
        self._dirty_mask = 0
        self.vendor = vendor
        self.model = model
        self.serial = serial
        self.admin_state = None
        self.aggr_port_id = None
        self.auto_negotiate = None
        self.chassis_id = None
        self.child_action = None
        self.config_qualifier = None
        self.ep_dn = None
        self.eq_type = None
        self.flt_aggr = None
        self.if_role = None
        self.if_type = None
        self.lc = None
        self.lic_gp = None
        self.lic_state = None
        self.locale = None
        self.name = None
        self.oper_state = None
        self.oper_state_reason = None
        self.peer_aggr_port_id = None
        self.peer_chassis_id = None
        self.peer_dn = None
        self.peer_port_id = None
        self.peer_slot_id = None
        self.port_id = None
        self.revision = None
        self.sacl = None
        self.slot_id = None
        self.status = None
        self.switch_id = None
        self.transport = None
        self.type = None

        ManagedObject.__init__(self, "FabricSwChPhEp", parent_mo_or_dn, **kwargs)

