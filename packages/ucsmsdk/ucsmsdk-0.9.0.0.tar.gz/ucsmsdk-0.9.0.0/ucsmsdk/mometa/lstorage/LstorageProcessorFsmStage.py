"""This module contains the general information for LstorageProcessorFsmStage ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class LstorageProcessorFsmStageConsts():
    LAST_UPDATE_TIME_ = ""
    NAME_CONFIGURE_ANALYZE_IMPACT = "ConfigureAnalyzeImpact"
    NAME_CONFIGURE_APPLY_CONFIG = "ConfigureApplyConfig"
    NAME_CONFIGURE_APPLY_DEFAULT_IDENTIFIERS = "ConfigureApplyDefaultIdentifiers"
    NAME_CONFIGURE_APPLY_IDENTIFIERS = "ConfigureApplyIdentifiers"
    NAME_CONFIGURE_APPLY_POLICIES = "ConfigureApplyPolicies"
    NAME_CONFIGURE_APPLY_TEMPLATE = "ConfigureApplyTemplate"
    NAME_CONFIGURE_BEGIN = "ConfigureBegin"
    NAME_CONFIGURE_EVALUATE_ASSOCIATION = "ConfigureEvaluateAssociation"
    NAME_CONFIGURE_FAIL = "ConfigureFail"
    NAME_CONFIGURE_RESOLVE_BOOT_CONFIG = "ConfigureResolveBootConfig"
    NAME_CONFIGURE_RESOLVE_DEFAULT_IDENTIFIERS = "ConfigureResolveDefaultIdentifiers"
    NAME_CONFIGURE_RESOLVE_DISTRIBUTABLE = "ConfigureResolveDistributable"
    NAME_CONFIGURE_RESOLVE_DISTRIBUTABLE_NAMES = "ConfigureResolveDistributableNames"
    NAME_CONFIGURE_RESOLVE_IDENTIFIERS = "ConfigureResolveIdentifiers"
    NAME_CONFIGURE_RESOLVE_IMAGES = "ConfigureResolveImages"
    NAME_CONFIGURE_RESOLVE_NETWORK_POLICIES = "ConfigureResolveNetworkPolicies"
    NAME_CONFIGURE_RESOLVE_POLICIES = "ConfigureResolvePolicies"
    NAME_CONFIGURE_RESOLVE_SCHEDULE = "ConfigureResolveSchedule"
    NAME_CONFIGURE_SUCCESS = "ConfigureSuccess"
    NAME_CONFIGURE_VALIDATE_POLICY_OWNERSHIP = "ConfigureValidatePolicyOwnership"
    NAME_CONFIGURE_WAIT_FOR_HAQUORUM = "ConfigureWaitForHAQuorum"
    NAME_CONFIGURE_WAIT_FOR_MAINT_PERMISSION = "ConfigureWaitForMaintPermission"
    NAME_CONFIGURE_WAIT_FOR_MAINT_WINDOW = "ConfigureWaitForMaintWindow"
    NAME_CONFIGURE_WAIT_FOR_OSINSTALL = "ConfigureWaitForOSInstall"
    NAME_CONFIGURE_WAIT_FOR_PLATFORM_BOOT = "ConfigureWaitForPlatformBoot"
    NAME_CONFIGURE_WAIT_FOR_PLATFORM_CONFIG = "ConfigureWaitForPlatformConfig"
    NAME_CONFIGURE_WAIT_FOR_SERVER_ASSOC = "ConfigureWaitForServerAssoc"
    NAME_NOP = "nop"
    STAGE_STATUS_FAIL = "fail"
    STAGE_STATUS_IN_PROGRESS = "inProgress"
    STAGE_STATUS_NOP = "nop"
    STAGE_STATUS_PENDING = "pending"
    STAGE_STATUS_SKIP = "skip"
    STAGE_STATUS_SUCCESS = "success"
    STAGE_STATUS_THROTTLED = "throttled"


class LstorageProcessorFsmStage(ManagedObject):
    """This is LstorageProcessorFsmStage class."""

    consts = LstorageProcessorFsmStageConsts()
    naming_props = set([u'name'])

    mo_meta = MoMeta("LstorageProcessorFsmStage", "lstorageProcessorFsmStage", "stage-[name]", VersionMeta.Version302c, "OutputOnly", 0xfL, [], [""], [u'lstorageProcessorFsm'], [], [None])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version302c, MoPropertyMeta.INTERNAL, None, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "descr": MoPropertyMeta("descr", "descr", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""[ !#$%&\(\)\*\+,\-\./:;\?@\[\]_\{\|\}~a-zA-Z0-9]{0,256}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, 0x2L, 0, 256, None, [], []), 
        "last_update_time": MoPropertyMeta("last_update_time", "lastUpdateTime", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""([0-9]){4}-([0-9]){2}-([0-9]){2}T([0-9]){2}:([0-9]){2}:([0-9]){2}((\.([0-9]){3})){0,1}""", [""], []), 
        "name": MoPropertyMeta("name", "name", "string", VersionMeta.Version302c, MoPropertyMeta.NAMING, None, None, None, None, ["ConfigureAnalyzeImpact", "ConfigureApplyConfig", "ConfigureApplyDefaultIdentifiers", "ConfigureApplyIdentifiers", "ConfigureApplyPolicies", "ConfigureApplyTemplate", "ConfigureBegin", "ConfigureEvaluateAssociation", "ConfigureFail", "ConfigureResolveBootConfig", "ConfigureResolveDefaultIdentifiers", "ConfigureResolveDistributable", "ConfigureResolveDistributableNames", "ConfigureResolveIdentifiers", "ConfigureResolveImages", "ConfigureResolveNetworkPolicies", "ConfigureResolvePolicies", "ConfigureResolveSchedule", "ConfigureSuccess", "ConfigureValidatePolicyOwnership", "ConfigureWaitForHAQuorum", "ConfigureWaitForMaintPermission", "ConfigureWaitForMaintWindow", "ConfigureWaitForOSInstall", "ConfigureWaitForPlatformBoot", "ConfigureWaitForPlatformConfig", "ConfigureWaitForServerAssoc", "nop"], []), 
        "order": MoPropertyMeta("order", "order", "ushort", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "retry": MoPropertyMeta("retry", "retry", "byte", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "stage_status": MoPropertyMeta("stage_status", "stageStatus", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, ["fail", "inProgress", "nop", "pending", "skip", "success", "throttled"], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version302c, MoPropertyMeta.READ_WRITE, 0x8L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
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

        ManagedObject.__init__(self, "LstorageProcessorFsmStage", parent_mo_or_dn, **kwargs)

