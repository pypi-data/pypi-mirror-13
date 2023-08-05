"""This module contains the general information for ComputePciCap ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class ComputePciCapConsts():
    ORDER_ASCENDING = "ascending"
    ORDER_ASCENDING_DUAL = "ascending-dual"
    ORDER_ASCENDING_EXTENDED = "ascending-extended"
    ORDER_ASCENDING_SEQ = "ascending-seq"
    ORDER_DESCENDING = "descending"


class ComputePciCap(ManagedObject):
    """This is ComputePciCap class."""

    consts = ComputePciCapConsts()
    naming_props = set([])

    mo_meta = MoMeta("ComputePciCap", "computePciCap", "pci", VersionMeta.Version111j, "InputOutput", 0x1ffL, [], ["read-only"], [u'equipmentBladeCapProvider', u'equipmentRackUnitCapProvider', u'equipmentServerUnitCapProvider'], [u'computePciSlotScanDef'], ["Get"])

    prop_meta = {
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version111j, MoPropertyMeta.INTERNAL, 0x2L, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "max_bus_id_per_slot": MoPropertyMeta("max_bus_id_per_slot", "maxBusIdPerSlot", "ushort", VersionMeta.Version204a, MoPropertyMeta.READ_WRITE, 0x8L, None, None, None, [], []), 
        "num_of_phys_slots": MoPropertyMeta("num_of_phys_slots", "numOfPhysSlots", "byte", VersionMeta.Version111j, MoPropertyMeta.READ_WRITE, 0x10L, None, None, None, [], []), 
        "order": MoPropertyMeta("order", "order", "string", VersionMeta.Version111j, MoPropertyMeta.READ_WRITE, 0x20L, None, None, None, ["ascending", "ascending-dual", "ascending-extended", "ascending-seq", "descending"], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, 0x40L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "starts_with": MoPropertyMeta("starts_with", "startsWith", "ushort", VersionMeta.Version111j, MoPropertyMeta.READ_WRITE, 0x80L, None, None, None, [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version111j, MoPropertyMeta.READ_WRITE, 0x100L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
    }

    prop_map = {
        "childAction": "child_action", 
        "dn": "dn", 
        "maxBusIdPerSlot": "max_bus_id_per_slot", 
        "numOfPhysSlots": "num_of_phys_slots", 
        "order": "order", 
        "rn": "rn", 
        "sacl": "sacl", 
        "startsWith": "starts_with", 
        "status": "status", 
    }

    def __init__(self, parent_mo_or_dn, **kwargs):
        self._dirty_mask = 0
        self.child_action = None
        self.max_bus_id_per_slot = None
        self.num_of_phys_slots = None
        self.order = None
        self.sacl = None
        self.starts_with = None
        self.status = None

        ManagedObject.__init__(self, "ComputePciCap", parent_mo_or_dn, **kwargs)

