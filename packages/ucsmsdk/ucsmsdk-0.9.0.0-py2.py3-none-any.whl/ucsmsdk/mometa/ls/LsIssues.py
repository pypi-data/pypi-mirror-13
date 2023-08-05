"""This module contains the general information for LsIssues ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class LsIssuesConsts():
    pass


class LsIssues(ManagedObject):
    """This is LsIssues class."""

    consts = LsIssuesConsts()
    naming_props = set([])

    mo_meta = MoMeta("LsIssues", "lsIssues", "config-issue", VersionMeta.Version221b, "InputOutput", 0x1fL, [], ["admin", "ls-compute", "ls-config", "ls-server"], [u'lsServer', u'lstorageProcessor'], [u'faultInst'], ["Get"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version221b, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "config_warnings": MoPropertyMeta("config_warnings", "configWarnings", "string", VersionMeta.Version222c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|not-applicable|kvm-mgmt-policy-unsupported),){0,2}(defaultValue|not-applicable|kvm-mgmt-policy-unsupported){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "iscsi_config_issues": MoPropertyMeta("iscsi_config_issues", "iscsiConfigIssues", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|not-applicable|static-target-mix|native-vlan|auto-target-auth|iscsi-config|missing-vlan|invalid-target-params|invalid-target-name|initiator-name|ip-addr-dhcp|init-target-passwd|auto-target-init|iscsi-initiator-ip-address|iqn-pool-name|vnic-name|no-luns|target-iscsilif-static-ip|unclassified|init-identity|target-name|no-vlan-ip|invalid-mac|iscsi-cardinality|allowed-vlan|internal-cfg-error|unresolvable-managed-target|auth-profile-same),){0,27}(defaultValue|not-applicable|static-target-mix|native-vlan|auto-target-auth|iscsi-config|missing-vlan|invalid-target-params|invalid-target-name|initiator-name|ip-addr-dhcp|init-target-passwd|auto-target-init|iscsi-initiator-ip-address|iqn-pool-name|vnic-name|no-luns|target-iscsilif-static-ip|unclassified|init-identity|target-name|no-vlan-ip|invalid-mac|iscsi-cardinality|allowed-vlan|internal-cfg-error|unresolvable-managed-target|auth-profile-same){0,1}""", [], []), 
        "network_config_issues": MoPropertyMeta("network_config_issues", "networkConfigIssues", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|not-applicable|network-feature-capability-mismatch|switch-virtual-if-capacity|conflicting-vlan-access|named-vlan-inaccessible|unsupported-multicast-policy|permit-unresolved|vlan-port-capacity|pinning-invalid),){0,9}(defaultValue|not-applicable|network-feature-capability-mismatch|switch-virtual-if-capacity|conflicting-vlan-access|named-vlan-inaccessible|unsupported-multicast-policy|permit-unresolved|vlan-port-capacity|pinning-invalid){0,1}""", [], []), 
        "prop_acl": MoPropertyMeta("prop_acl", "propAcl", "ulong", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, 0x8L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "server_config_issues": MoPropertyMeta("server_config_issues", "serverConfigIssues", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|not-applicable|insufficient-power-budget|server-position-requirement|boot-configuration-unsupported|ivb-bios-downgrade-restriction|compute-undiscovered|power-group-requirement|imgsec-policy-invalid|soft-pinning-vlan-mismatch|missing-firmware-image|resource-ownership-conflict|boot-order-pxe|vmedia-policy-unsupported|insufficient-resources|mac-address-assignment|remote-service-profile|server-feature-capability-mismatch|boot-order-jbod-image-path|incompat-bios-for-sriov-vnics|processor-requirement|provsrv-policy-invalid|cimc-downgrade-restriction|board-controller-update-unsupported|non-interrupt-fsm-running|boot-order-san-image-path|bootip-policy-invalid|boot-policy-vmedia-invalid|memory-requirement|system-uuid-assignment|domain-requirement|qualified-pool-without-binding|boot-configuration-invalid|incompatible-bios-image|remote-policy|qos-policy-invalid|ivb-cimc-downgrade-restriction|compute-unavailable|physical-requirement|hostimg-policy-invalid|vmedia-mount-config-invalid|migration|wwnn-derivation-from-vhba|duplicate-address-conflict|boot-order-iscsi),){0,44}(defaultValue|not-applicable|insufficient-power-budget|server-position-requirement|boot-configuration-unsupported|ivb-bios-downgrade-restriction|compute-undiscovered|power-group-requirement|imgsec-policy-invalid|soft-pinning-vlan-mismatch|missing-firmware-image|resource-ownership-conflict|boot-order-pxe|vmedia-policy-unsupported|insufficient-resources|mac-address-assignment|remote-service-profile|server-feature-capability-mismatch|boot-order-jbod-image-path|incompat-bios-for-sriov-vnics|processor-requirement|provsrv-policy-invalid|cimc-downgrade-restriction|board-controller-update-unsupported|non-interrupt-fsm-running|boot-order-san-image-path|bootip-policy-invalid|boot-policy-vmedia-invalid|memory-requirement|system-uuid-assignment|domain-requirement|qualified-pool-without-binding|boot-configuration-invalid|incompatible-bios-image|remote-policy|qos-policy-invalid|ivb-cimc-downgrade-restriction|compute-unavailable|physical-requirement|hostimg-policy-invalid|vmedia-mount-config-invalid|migration|wwnn-derivation-from-vhba|duplicate-address-conflict|boot-order-iscsi){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version221b, MoPropertyMeta.READ_WRITE, 0x10L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "storage_config_issues": MoPropertyMeta("storage_config_issues", "storageConfigIssues", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|not-applicable|flexflash-metadata|unsupported-disk-controller-config|unsupported-expand-to-available|unsupported-use-remaining-disks|zone-capacity|duplicated-lun-name|unsupported-hotspare-change|unsupported-vd-modification|disk-role-mismatch|missing-raid-key|orphaned-lun-ref-missing|virtual-drive-access-denied|destructive-local-disk-config|storage-feature-capability-mismatch|insufficient-disks|conflicting-lun-config|unsupported-global-hotspares|drive-cache-not-supported|flexflash-controller|unsupported-controller|invalid-storage-profile-binding|lun-in-use|incompatible-disk-types|storage-path-configuration-error|disk-type-mismatch|orphaned-lun-ref-access-denied|virtual-drive-deletion-in-progress|unsupported-raid-level|incomplete-lun-config|unsupported-order|embedded-controller-not-supported|incompatible-number-of-local-disks|flexflash-card|unsupported-destructive-change|invalid-local-lun-disk-policy-reference|set-proper-order|wwnn-assignment|unsupported-orphan-lun-modification|unsupported-lun-map-modification|unsupported-write-cache-policy|unsupported-io-policy|insufficient-storage-space|order-should-be-unique|virtual-drive-capacity|incompatible-raid-level),){0,46}(defaultValue|not-applicable|flexflash-metadata|unsupported-disk-controller-config|unsupported-expand-to-available|unsupported-use-remaining-disks|zone-capacity|duplicated-lun-name|unsupported-hotspare-change|unsupported-vd-modification|disk-role-mismatch|missing-raid-key|orphaned-lun-ref-missing|virtual-drive-access-denied|destructive-local-disk-config|storage-feature-capability-mismatch|insufficient-disks|conflicting-lun-config|unsupported-global-hotspares|drive-cache-not-supported|flexflash-controller|unsupported-controller|invalid-storage-profile-binding|lun-in-use|incompatible-disk-types|storage-path-configuration-error|disk-type-mismatch|orphaned-lun-ref-access-denied|virtual-drive-deletion-in-progress|unsupported-raid-level|incomplete-lun-config|unsupported-order|embedded-controller-not-supported|incompatible-number-of-local-disks|flexflash-card|unsupported-destructive-change|invalid-local-lun-disk-policy-reference|set-proper-order|wwnn-assignment|unsupported-orphan-lun-modification|unsupported-lun-map-modification|unsupported-write-cache-policy|unsupported-io-policy|insufficient-storage-space|order-should-be-unique|virtual-drive-capacity|incompatible-raid-level){0,1}""", [], []), 
        "vnic_config_issues": MoPropertyMeta("vnic_config_issues", "vnicConfigIssues", "string", VersionMeta.Version221b, MoPropertyMeta.READ_ONLY, None, None, None, r"""((defaultValue|not-applicable|adaptor-protected-eth-capability|vif-resources-overprovisioned|ungrouped-domain|unsupported-nvgre|unresolved-remote-vlan-name|invalid-wwn|service-profile-virtualization-conflict|unsupported-roce-netflow|unsupported-vxlan-netflow|fcoe-capacity|wwpn-derivation-virtualized-port|unresolved-vlan-name|vnic-virtualization-netflow-conflict|unsupported-vxlan-usnic|pinning-vlan-mismatch|adaptor-requirement|vnic-not-ha-ready|missing-ipv4-inband-mgmt-addr|unsupported-nvgre-dynamic-vnic|unresolved-remote-vsan-name|mac-derivation-virtualized-port|vnic-virtualization-conflict|unsupported-roce|unsupported-nvgre-netflow|vnic-vlan-assignment-error|insufficient-vhba-capacity|inaccessible-vlan|unable-to-update-ucsm|soft-pinning-vlan-mismatch|unsupported-nvgre-vmq|connection-placement|vnic-vcon-provisioning-change|missing-ipv6-inband-mgmt-addr|unsupported-nvgre-usnic|missing-primary-vlan|adaptor-fcoe-capability|vfc-vnic-pvlan-conflict|virtualization-not-supported|unsupported-vxlan|unresolved-vsan-name|insufficient-vnic-capacity|unassociated-vlan|unsupported-roce-vmq|unsupported-vxlan-vmq|dynamic-vf-vnic|wwpn-assignment|missing-ipv4-addr|unsupported-vxlan-dynamic-vnic|pinned-target-misconfig),){0,50}(defaultValue|not-applicable|adaptor-protected-eth-capability|vif-resources-overprovisioned|ungrouped-domain|unsupported-nvgre|unresolved-remote-vlan-name|invalid-wwn|service-profile-virtualization-conflict|unsupported-roce-netflow|unsupported-vxlan-netflow|fcoe-capacity|wwpn-derivation-virtualized-port|unresolved-vlan-name|vnic-virtualization-netflow-conflict|unsupported-vxlan-usnic|pinning-vlan-mismatch|adaptor-requirement|vnic-not-ha-ready|missing-ipv4-inband-mgmt-addr|unsupported-nvgre-dynamic-vnic|unresolved-remote-vsan-name|mac-derivation-virtualized-port|vnic-virtualization-conflict|unsupported-roce|unsupported-nvgre-netflow|vnic-vlan-assignment-error|insufficient-vhba-capacity|inaccessible-vlan|unable-to-update-ucsm|soft-pinning-vlan-mismatch|unsupported-nvgre-vmq|connection-placement|vnic-vcon-provisioning-change|missing-ipv6-inband-mgmt-addr|unsupported-nvgre-usnic|missing-primary-vlan|adaptor-fcoe-capability|vfc-vnic-pvlan-conflict|virtualization-not-supported|unsupported-vxlan|unresolved-vsan-name|insufficient-vnic-capacity|unassociated-vlan|unsupported-roce-vmq|unsupported-vxlan-vmq|dynamic-vf-vnic|wwpn-assignment|missing-ipv4-addr|unsupported-vxlan-dynamic-vnic|pinned-target-misconfig){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "configWarnings": "config_warnings", 
        "dn": "dn", 
        "iscsiConfigIssues": "iscsi_config_issues", 
        "networkConfigIssues": "network_config_issues", 
        "propAcl": "prop_acl", 
        "rn": "rn", 
        "sacl": "sacl", 
        "serverConfigIssues": "server_config_issues", 
        "status": "status", 
        "storageConfigIssues": "storage_config_issues", 
        "vnicConfigIssues": "vnic_config_issues", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.config_warnings = None
        self.iscsi_config_issues = None
        self.network_config_issues = None
        self.prop_acl = None
        self.sacl = None
        self.server_config_issues = None
        self.status = None
        self.storage_config_issues = None
        self.vnic_config_issues = None

        ManagedObject.__init__(self, "LsIssues", parent_mo_or_dn, **kwargs)

