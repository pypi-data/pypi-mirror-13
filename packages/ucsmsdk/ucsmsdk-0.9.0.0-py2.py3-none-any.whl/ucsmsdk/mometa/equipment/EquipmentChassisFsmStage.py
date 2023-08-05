"""This module contains the general information for EquipmentChassisFsmStage ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class EquipmentChassisFsmStageConsts():
    LAST_UPDATE_TIME_ = ""
    NAME_DYNAMIC_REALLOCATION_BEGIN = "DynamicReallocationBegin"
    NAME_DYNAMIC_REALLOCATION_CONFIG = "DynamicReallocationConfig"
    NAME_DYNAMIC_REALLOCATION_FAIL = "DynamicReallocationFail"
    NAME_DYNAMIC_REALLOCATION_SUCCESS = "DynamicReallocationSuccess"
    NAME_OOB_STORAGE_ADMIN_CFG_BEGIN = "OobStorageAdminCfgBegin"
    NAME_OOB_STORAGE_ADMIN_CFG_FAIL = "OobStorageAdminCfgFail"
    NAME_OOB_STORAGE_ADMIN_CFG_OOB_STORAGE_CONFIG = "OobStorageAdminCfgOobStorageConfig"
    NAME_OOB_STORAGE_ADMIN_CFG_SUCCESS = "OobStorageAdminCfgSuccess"
    NAME_POWER_CAP_BEGIN = "PowerCapBegin"
    NAME_POWER_CAP_CONFIG = "PowerCapConfig"
    NAME_POWER_CAP_FAIL = "PowerCapFail"
    NAME_POWER_CAP_SUCCESS = "PowerCapSuccess"
    NAME_PSU_POLICY_CONFIG_BEGIN = "PsuPolicyConfigBegin"
    NAME_PSU_POLICY_CONFIG_EXECUTE = "PsuPolicyConfigExecute"
    NAME_PSU_POLICY_CONFIG_FAIL = "PsuPolicyConfigFail"
    NAME_PSU_POLICY_CONFIG_SUCCESS = "PsuPolicyConfigSuccess"
    NAME_REMOVE_CHASSIS_BEGIN = "RemoveChassisBegin"
    NAME_REMOVE_CHASSIS_CLEANUP_VNICS_LOCAL = "RemoveChassisCleanupVnicsLocal"
    NAME_REMOVE_CHASSIS_CLEANUP_VNICS_PEER = "RemoveChassisCleanupVnicsPeer"
    NAME_REMOVE_CHASSIS_DECOMISSION = "RemoveChassisDecomission"
    NAME_REMOVE_CHASSIS_DISABLE_END_POINT = "RemoveChassisDisableEndPoint"
    NAME_REMOVE_CHASSIS_FAIL = "RemoveChassisFail"
    NAME_REMOVE_CHASSIS_SUCCESS = "RemoveChassisSuccess"
    NAME_REMOVE_CHASSIS_UN_IDENTIFY_LOCAL = "RemoveChassisUnIdentifyLocal"
    NAME_REMOVE_CHASSIS_UN_IDENTIFY_PEER = "RemoveChassisUnIdentifyPeer"
    NAME_REMOVE_CHASSIS_WAIT = "RemoveChassisWait"
    NAME_NOP = "nop"
    STAGE_STATUS_FAIL = "fail"
    STAGE_STATUS_IN_PROGRESS = "inProgress"
    STAGE_STATUS_NOP = "nop"
    STAGE_STATUS_PENDING = "pending"
    STAGE_STATUS_SKIP = "skip"
    STAGE_STATUS_SUCCESS = "success"
    STAGE_STATUS_THROTTLED = "throttled"


class EquipmentChassisFsmStage(ManagedObject):
    """This is EquipmentChassisFsmStage class."""

    consts = EquipmentChassisFsmStageConsts()
    naming_props = set([u'name'])

    mo_meta = MoMeta("EquipmentChassisFsmStage", "equipmentChassisFsmStage", "stage-[name]", VersionMeta.Version211a, "OutputOnly", 0xfL, [], [""], [u'equipmentChassisFsm'], [], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version211a, MoPropertyMeta.INTERNAL, None, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "descr": MoPropertyMeta("descr", "descr", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, r"""[ !#$%&\(\)\*\+,\-\./:;\?@\[\]_\{\|\}~a-zA-Z0-9]{0,256}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, 0x2L, 0, 256, None, [], []), 
        "last_update_time": MoPropertyMeta("last_update_time", "lastUpdateTime", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, r"""([0-9]){4}-([0-9]){2}-([0-9]){2}T([0-9]){2}:([0-9]){2}:([0-9]){2}((\.([0-9]){3})){0,1}""", [""], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version211a, MoPropertyMeta.NAMING, None, None, None, None, ["DynamicReallocationBegin", "DynamicReallocationConfig", "DynamicReallocationFail", "DynamicReallocationSuccess", "OobStorageAdminCfgBegin", "OobStorageAdminCfgFail", "OobStorageAdminCfgOobStorageConfig", "OobStorageAdminCfgSuccess", "PowerCapBegin", "PowerCapConfig", "PowerCapFail", "PowerCapSuccess", "PsuPolicyConfigBegin", "PsuPolicyConfigExecute", "PsuPolicyConfigFail", "PsuPolicyConfigSuccess", "RemoveChassisBegin", "RemoveChassisCleanupVnicsLocal", "RemoveChassisCleanupVnicsPeer", "RemoveChassisDecomission", "RemoveChassisDisableEndPoint", "RemoveChassisFail", "RemoveChassisSuccess", "RemoveChassisUnIdentifyLocal", "RemoveChassisUnIdentifyPeer", "RemoveChassisWait", "nop"], []), 
        "order": MoPropertyMeta("order", "order", "ushort", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "retry": MoPropertyMeta("retry", "retry", "byte", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "stage_status": MoPropertyMeta("stage_status", "stageStatus", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, None, ["fail", "inProgress", "nop", "pending", "skip", "success", "throttled"], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version211a, MoPropertyMeta.READ_WRITE, 0x8L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "descr": "descr", 
        "dn": "dn", 
        "lastUpdateTime": "last_update_time", 
        "name": "name", 
        "order": "order", 
        "retry": "retry", 
        "rn": "rn", 
        "sacl": "sacl", 
        "stageStatus": "stage_status", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, name, **kwargs):
        self._dirty_mask = 0
        self.name = name
        self.child_action = None
        self.descr = None
        self.last_update_time = None
        self.order = None
        self.retry = None
        self.sacl = None
        self.stage_status = None
        self.status = None

        ManagedObject.__init__(self, "EquipmentChassisFsmStage", parent_mo_or_dn, **kwargs)

