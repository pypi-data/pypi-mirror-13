"""This module contains the general information for MgmtControllerFsmStage ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class MgmtControllerFsmStageConsts():
    LAST_UPDATE_TIME_ = ""
    NAME_ACTIVATE_ADAPTOR_ACTIVATE = "ActivateAdaptorActivate"
    NAME_ACTIVATE_ADAPTOR_BEGIN = "ActivateAdaptorBegin"
    NAME_ACTIVATE_ADAPTOR_FAIL = "ActivateAdaptorFail"
    NAME_ACTIVATE_ADAPTOR_POLL_ACTIVATE_STATUS = "ActivateAdaptorPollActivateStatus"
    NAME_ACTIVATE_ADAPTOR_POWER_OFF_SERVERS = "ActivateAdaptorPowerOffServers"
    NAME_ACTIVATE_ADAPTOR_RESET = "ActivateAdaptorReset"
    NAME_ACTIVATE_ADAPTOR_SERVERS_POWER_OFF_COMPLETION = "ActivateAdaptorServersPowerOffCompletion"
    NAME_ACTIVATE_ADAPTOR_SUCCESS = "ActivateAdaptorSuccess"
    NAME_ACTIVATE_BMCACTIVATE = "ActivateBMCActivate"
    NAME_ACTIVATE_BMCBEGIN = "ActivateBMCBegin"
    NAME_ACTIVATE_BMCFAIL = "ActivateBMCFail"
    NAME_ACTIVATE_BMCRESET = "ActivateBMCReset"
    NAME_ACTIVATE_BMCSUCCESS = "ActivateBMCSuccess"
    NAME_ACTIVATE_CMCACTIVATE = "ActivateCMCActivate"
    NAME_ACTIVATE_CMCBEGIN = "ActivateCMCBegin"
    NAME_ACTIVATE_CMCFAIL = "ActivateCMCFail"
    NAME_ACTIVATE_CMCPOLL_ACTIVATION = "ActivateCMCPollActivation"
    NAME_ACTIVATE_CMCRESET = "ActivateCMCReset"
    NAME_ACTIVATE_CMCSUCCESS = "ActivateCMCSuccess"
    NAME_ACTIVATE_IOMACTIVATE = "ActivateIOMActivate"
    NAME_ACTIVATE_IOMBEGIN = "ActivateIOMBegin"
    NAME_ACTIVATE_IOMFAIL = "ActivateIOMFail"
    NAME_ACTIVATE_IOMRESET = "ActivateIOMReset"
    NAME_ACTIVATE_IOMSUCCESS = "ActivateIOMSuccess"
    NAME_EXT_MGMT_IF_CONFIG_BEGIN = "ExtMgmtIfConfigBegin"
    NAME_EXT_MGMT_IF_CONFIG_FAIL = "ExtMgmtIfConfigFail"
    NAME_EXT_MGMT_IF_CONFIG_PRIMARY = "ExtMgmtIfConfigPrimary"
    NAME_EXT_MGMT_IF_CONFIG_SECONDARY = "ExtMgmtIfConfigSecondary"
    NAME_EXT_MGMT_IF_CONFIG_SUCCESS = "ExtMgmtIfConfigSuccess"
    NAME_EXT_MGMT_INTERFACE_CONFIG_ACTIVE = "ExtMgmtInterfaceConfigActive"
    NAME_EXT_MGMT_INTERFACE_CONFIG_BEGIN = "ExtMgmtInterfaceConfigBegin"
    NAME_EXT_MGMT_INTERFACE_CONFIG_CIMCVLAN_CFG_LOCAL = "ExtMgmtInterfaceConfigCIMCVlanCfgLocal"
    NAME_EXT_MGMT_INTERFACE_CONFIG_CIMCVLAN_CFG_PEER = "ExtMgmtInterfaceConfigCIMCVlanCfgPeer"
    NAME_EXT_MGMT_INTERFACE_CONFIG_CMCVLAN_CFG = "ExtMgmtInterfaceConfigCMCVlanCfg"
    NAME_EXT_MGMT_INTERFACE_CONFIG_CMCVLAN_CFG_PEER = "ExtMgmtInterfaceConfigCMCVlanCfgPeer"
    NAME_EXT_MGMT_INTERFACE_CONFIG_FAIL = "ExtMgmtInterfaceConfigFail"
    NAME_EXT_MGMT_INTERFACE_CONFIG_SUCCESS = "ExtMgmtInterfaceConfigSuccess"
    NAME_LOCK_CONFIG_BEGIN = "LockConfigBegin"
    NAME_LOCK_CONFIG_FAIL = "LockConfigFail"
    NAME_LOCK_CONFIG_POWER_BUTTON_LOCK_CONFIG = "LockConfigPowerButtonLockConfig"
    NAME_LOCK_CONFIG_SUCCESS = "LockConfigSuccess"
    NAME_ONLINE_BEGIN = "OnlineBegin"
    NAME_ONLINE_BMC_CONFIGURE_CONN_LOCAL = "OnlineBmcConfigureConnLocal"
    NAME_ONLINE_BMC_CONFIGURE_CONN_PEER = "OnlineBmcConfigureConnPeer"
    NAME_ONLINE_FAIL = "OnlineFail"
    NAME_ONLINE_SUCCESS = "OnlineSuccess"
    NAME_ONLINE_SW_CONFIGURE_CONN_LOCAL = "OnlineSwConfigureConnLocal"
    NAME_ONLINE_SW_CONFIGURE_CONN_PEER = "OnlineSwConfigureConnPeer"
    NAME_POWER_BUDGET_RECLAIM_CONFIG_BEGIN = "PowerBudgetReclaimConfigBegin"
    NAME_POWER_BUDGET_RECLAIM_CONFIG_FAIL = "PowerBudgetReclaimConfigFail"
    NAME_POWER_BUDGET_RECLAIM_CONFIG_POWER_OFF_RECLAIM = "PowerBudgetReclaimConfigPowerOffReclaim"
    NAME_POWER_BUDGET_RECLAIM_CONFIG_POWER_OFF_WAIT = "PowerBudgetReclaimConfigPowerOffWait"
    NAME_POWER_BUDGET_RECLAIM_CONFIG_SUCCESS = "PowerBudgetReclaimConfigSuccess"
    NAME_REGISTRY_CONFIG_BEGIN = "RegistryConfigBegin"
    NAME_REGISTRY_CONFIG_FAIL = "RegistryConfigFail"
    NAME_REGISTRY_CONFIG_REMOVE = "RegistryConfigRemove"
    NAME_REGISTRY_CONFIG_SUCCESS = "RegistryConfigSuccess"
    NAME_SYS_CONFIG_BEGIN = "SysConfigBegin"
    NAME_SYS_CONFIG_FAIL = "SysConfigFail"
    NAME_SYS_CONFIG_PRIMARY = "SysConfigPrimary"
    NAME_SYS_CONFIG_SECONDARY = "SysConfigSecondary"
    NAME_SYS_CONFIG_SUCCESS = "SysConfigSuccess"
    NAME_UPDATE_ADAPTOR_BEGIN = "UpdateAdaptorBegin"
    NAME_UPDATE_ADAPTOR_FAIL = "UpdateAdaptorFail"
    NAME_UPDATE_ADAPTOR_POLL_UPDATE_STATUS = "UpdateAdaptorPollUpdateStatus"
    NAME_UPDATE_ADAPTOR_SUCCESS = "UpdateAdaptorSuccess"
    NAME_UPDATE_ADAPTOR_UPDATE_REQUEST = "UpdateAdaptorUpdateRequest"
    NAME_UPDATE_BMCBEGIN = "UpdateBMCBegin"
    NAME_UPDATE_BMCFAIL = "UpdateBMCFail"
    NAME_UPDATE_BMCPOLL_UPDATE_STATUS = "UpdateBMCPollUpdateStatus"
    NAME_UPDATE_BMCSUCCESS = "UpdateBMCSuccess"
    NAME_UPDATE_BMCUPDATE_REQUEST = "UpdateBMCUpdateRequest"
    NAME_UPDATE_BOARD_CONTROLLER_BEGIN = "UpdateBoardControllerBegin"
    NAME_UPDATE_BOARD_CONTROLLER_FAIL = "UpdateBoardControllerFail"
    NAME_UPDATE_BOARD_CONTROLLER_POLL_UPDATE_STATUS = "UpdateBoardControllerPollUpdateStatus"
    NAME_UPDATE_BOARD_CONTROLLER_POWER_OFF_SERVERS = "UpdateBoardControllerPowerOffServers"
    NAME_UPDATE_BOARD_CONTROLLER_PREPARE_FOR_UPDATE = "UpdateBoardControllerPrepareForUpdate"
    NAME_UPDATE_BOARD_CONTROLLER_SERVERS_POWER_OFF_COMPLETION = "UpdateBoardControllerServersPowerOffCompletion"
    NAME_UPDATE_BOARD_CONTROLLER_SUCCESS = "UpdateBoardControllerSuccess"
    NAME_UPDATE_BOARD_CONTROLLER_UPDATE_REQUEST = "UpdateBoardControllerUpdateRequest"
    NAME_UPDATE_CMCBEGIN = "UpdateCMCBegin"
    NAME_UPDATE_CMCFAIL = "UpdateCMCFail"
    NAME_UPDATE_CMCPOLL_UPDATE_STATUS = "UpdateCMCPollUpdateStatus"
    NAME_UPDATE_CMCSUCCESS = "UpdateCMCSuccess"
    NAME_UPDATE_CMCUPDATE_REQUEST = "UpdateCMCUpdateRequest"
    NAME_UPDATE_IOMBEGIN = "UpdateIOMBegin"
    NAME_UPDATE_IOMCOPY_IOMIMG_TO_SUB = "UpdateIOMCopyIOMImgToSub"
    NAME_UPDATE_IOMCOPY_IMG_FROM_REP = "UpdateIOMCopyImgFromRep"
    NAME_UPDATE_IOMFAIL = "UpdateIOMFail"
    NAME_UPDATE_IOMPOLL_UPDATE_STATUS = "UpdateIOMPollUpdateStatus"
    NAME_UPDATE_IOMSUCCESS = "UpdateIOMSuccess"
    NAME_UPDATE_IOMUPDATE_REQUEST = "UpdateIOMUpdateRequest"
    NAME_UPDATE_RAID_CONTROLLER_ACTIVATE = "UpdateRaidControllerActivate"
    NAME_UPDATE_RAID_CONTROLLER_BEGIN = "UpdateRaidControllerBegin"
    NAME_UPDATE_RAID_CONTROLLER_FAIL = "UpdateRaidControllerFail"
    NAME_UPDATE_RAID_CONTROLLER_POLL_ACTIVATION = "UpdateRaidControllerPollActivation"
    NAME_UPDATE_RAID_CONTROLLER_POLL_UPDATE_STATUS = "UpdateRaidControllerPollUpdateStatus"
    NAME_UPDATE_RAID_CONTROLLER_POWER_OFF_SERVERS = "UpdateRaidControllerPowerOffServers"
    NAME_UPDATE_RAID_CONTROLLER_SERVERS_POWER_OFF_COMPLETION = "UpdateRaidControllerServersPowerOffCompletion"
    NAME_UPDATE_RAID_CONTROLLER_SUCCESS = "UpdateRaidControllerSuccess"
    NAME_UPDATE_RAID_CONTROLLER_UPDATE_REQUEST = "UpdateRaidControllerUpdateRequest"
    NAME_UPDATE_SWITCH_BEGIN = "UpdateSwitchBegin"
    NAME_UPDATE_SWITCH_COPY_TO_LOCAL = "UpdateSwitchCopyToLocal"
    NAME_UPDATE_SWITCH_COPY_TO_PEER = "UpdateSwitchCopyToPeer"
    NAME_UPDATE_SWITCH_FAIL = "UpdateSwitchFail"
    NAME_UPDATE_SWITCH_RESET_LOCAL = "UpdateSwitchResetLocal"
    NAME_UPDATE_SWITCH_RESET_REMOTE = "UpdateSwitchResetRemote"
    NAME_UPDATE_SWITCH_SUCCESS = "UpdateSwitchSuccess"
    NAME_UPDATE_SWITCH_UPDATE_LOCAL = "UpdateSwitchUpdateLocal"
    NAME_UPDATE_SWITCH_UPDATE_REMOTE = "UpdateSwitchUpdateRemote"
    NAME_UPDATE_SWITCH_VERIFY_LOCAL = "UpdateSwitchVerifyLocal"
    NAME_UPDATE_SWITCH_VERIFY_REMOTE = "UpdateSwitchVerifyRemote"
    NAME_UPDATE_UCSMANAGER_BEGIN = "UpdateUCSManagerBegin"
    NAME_UPDATE_UCSMANAGER_COPY_EXT_TO_LOCAL = "UpdateUCSManagerCopyExtToLocal"
    NAME_UPDATE_UCSMANAGER_COPY_EXT_TO_PEER = "UpdateUCSManagerCopyExtToPeer"
    NAME_UPDATE_UCSMANAGER_EXECUTE = "UpdateUCSManagerExecute"
    NAME_UPDATE_UCSMANAGER_FAIL = "UpdateUCSManagerFail"
    NAME_UPDATE_UCSMANAGER_START = "UpdateUCSManagerStart"
    NAME_UPDATE_UCSMANAGER_SUCCESS = "UpdateUCSManagerSuccess"
    NAME_NOP = "nop"
    STAGE_STATUS_FAIL = "fail"
    STAGE_STATUS_IN_PROGRESS = "inProgress"
    STAGE_STATUS_NOP = "nop"
    STAGE_STATUS_PENDING = "pending"
    STAGE_STATUS_SKIP = "skip"
    STAGE_STATUS_SUCCESS = "success"
    STAGE_STATUS_THROTTLED = "throttled"


class MgmtControllerFsmStage(ManagedObject):
    """This is MgmtControllerFsmStage class."""

    consts = MgmtControllerFsmStageConsts()
    naming_props = set([u'name'])

    mo_meta = MoMeta("MgmtControllerFsmStage", "mgmtControllerFsmStage", "stage-[name]", VersionMeta.Version211a, "OutputOnly", 0xfL, [], [""], [u'mgmtControllerFsm'], [], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version211a, MoPropertyMeta.INTERNAL, None, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "descr": MoPropertyMeta("descr", "descr", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, r"""[ !#$%&\(\)\*\+,\-\./:;\?@\[\]_\{\|\}~a-zA-Z0-9]{0,256}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, 0x2L, 0, 256, None, [], []), 
        "last_update_time": MoPropertyMeta("last_update_time", "lastUpdateTime", "string", VersionMeta.Version211a, MoPropertyMeta.READ_ONLY, None, None, None, r"""([0-9]){4}-([0-9]){2}-([0-9]){2}T([0-9]){2}:([0-9]){2}:([0-9]){2}((\.([0-9]){3})){0,1}""", [""], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version211a, MoPropertyMeta.NAMING, None, None, None, None, ["ActivateAdaptorActivate", "ActivateAdaptorBegin", "ActivateAdaptorFail", "ActivateAdaptorPollActivateStatus", "ActivateAdaptorPowerOffServers", "ActivateAdaptorReset", "ActivateAdaptorServersPowerOffCompletion", "ActivateAdaptorSuccess", "ActivateBMCActivate", "ActivateBMCBegin", "ActivateBMCFail", "ActivateBMCReset", "ActivateBMCSuccess", "ActivateCMCActivate", "ActivateCMCBegin", "ActivateCMCFail", "ActivateCMCPollActivation", "ActivateCMCReset", "ActivateCMCSuccess", "ActivateIOMActivate", "ActivateIOMBegin", "ActivateIOMFail", "ActivateIOMReset", "ActivateIOMSuccess", "ExtMgmtIfConfigBegin", "ExtMgmtIfConfigFail", "ExtMgmtIfConfigPrimary", "ExtMgmtIfConfigSecondary", "ExtMgmtIfConfigSuccess", "ExtMgmtInterfaceConfigActive", "ExtMgmtInterfaceConfigBegin", "ExtMgmtInterfaceConfigCIMCVlanCfgLocal", "ExtMgmtInterfaceConfigCIMCVlanCfgPeer", "ExtMgmtInterfaceConfigCMCVlanCfg", "ExtMgmtInterfaceConfigCMCVlanCfgPeer", "ExtMgmtInterfaceConfigFail", "ExtMgmtInterfaceConfigSuccess", "LockConfigBegin", "LockConfigFail", "LockConfigPowerButtonLockConfig", "LockConfigSuccess", "OnlineBegin", "OnlineBmcConfigureConnLocal", "OnlineBmcConfigureConnPeer", "OnlineFail", "OnlineSuccess", "OnlineSwConfigureConnLocal", "OnlineSwConfigureConnPeer", "PowerBudgetReclaimConfigBegin", "PowerBudgetReclaimConfigFail", "PowerBudgetReclaimConfigPowerOffReclaim", "PowerBudgetReclaimConfigPowerOffWait", "PowerBudgetReclaimConfigSuccess", "RegistryConfigBegin", "RegistryConfigFail", "RegistryConfigRemove", "RegistryConfigSuccess", "SysConfigBegin", "SysConfigFail", "SysConfigPrimary", "SysConfigSecondary", "SysConfigSuccess", "UpdateAdaptorBegin", "UpdateAdaptorFail", "UpdateAdaptorPollUpdateStatus", "UpdateAdaptorSuccess", "UpdateAdaptorUpdateRequest", "UpdateBMCBegin", "UpdateBMCFail", "UpdateBMCPollUpdateStatus", "UpdateBMCSuccess", "UpdateBMCUpdateRequest", "UpdateBoardControllerBegin", "UpdateBoardControllerFail", "UpdateBoardControllerPollUpdateStatus", "UpdateBoardControllerPowerOffServers", "UpdateBoardControllerPrepareForUpdate", "UpdateBoardControllerServersPowerOffCompletion", "UpdateBoardControllerSuccess", "UpdateBoardControllerUpdateRequest", "UpdateCMCBegin", "UpdateCMCFail", "UpdateCMCPollUpdateStatus", "UpdateCMCSuccess", "UpdateCMCUpdateRequest", "UpdateIOMBegin", "UpdateIOMCopyIOMImgToSub", "UpdateIOMCopyImgFromRep", "UpdateIOMFail", "UpdateIOMPollUpdateStatus", "UpdateIOMSuccess", "UpdateIOMUpdateRequest", "UpdateRaidControllerActivate", "UpdateRaidControllerBegin", "UpdateRaidControllerFail", "UpdateRaidControllerPollActivation", "UpdateRaidControllerPollUpdateStatus", "UpdateRaidControllerPowerOffServers", "UpdateRaidControllerServersPowerOffCompletion", "UpdateRaidControllerSuccess", "UpdateRaidControllerUpdateRequest", "UpdateSwitchBegin", "UpdateSwitchCopyToLocal", "UpdateSwitchCopyToPeer", "UpdateSwitchFail", "UpdateSwitchResetLocal", "UpdateSwitchResetRemote", "UpdateSwitchSuccess", "UpdateSwitchUpdateLocal", "UpdateSwitchUpdateRemote", "UpdateSwitchVerifyLocal", "UpdateSwitchVerifyRemote", "UpdateUCSManagerBegin", "UpdateUCSManagerCopyExtToLocal", "UpdateUCSManagerCopyExtToPeer", "UpdateUCSManagerExecute", "UpdateUCSManagerFail", "UpdateUCSManagerStart", "UpdateUCSManagerSuccess", "nop"], []), 
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

        ManagedObject.__init__(self, "MgmtControllerFsmStage", parent_mo_or_dn, **kwargs)

