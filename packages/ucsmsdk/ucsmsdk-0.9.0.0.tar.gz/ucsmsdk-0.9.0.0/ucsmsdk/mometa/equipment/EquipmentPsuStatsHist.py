"""This module contains the general information for EquipmentPsuStatsHist ManagedObject."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ucsmo import ManagedObject
from ucscoremeta import UcsVersion, MoPropertyMeta, MoMeta
from ucsmeta import VersionMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class EquipmentPsuStatsHistConsts():
    AMBIENT_TEMP_NOT_APPLICABLE = "not-applicable"
    AMBIENT_TEMP_AVG_NOT_APPLICABLE = "not-applicable"
    AMBIENT_TEMP_MAX_NOT_APPLICABLE = "not-applicable"
    AMBIENT_TEMP_MIN_NOT_APPLICABLE = "not-applicable"
    MOST_RECENT_FALSE = "false"
    MOST_RECENT_NO = "no"
    MOST_RECENT_TRUE = "true"
    MOST_RECENT_YES = "yes"
    SUSPECT_FALSE = "false"
    SUSPECT_NO = "no"
    SUSPECT_TRUE = "true"
    SUSPECT_YES = "yes"


class EquipmentPsuStatsHist(ManagedObject):
    """This is EquipmentPsuStatsHist class."""

    consts = EquipmentPsuStatsHistConsts()
    naming_props = set([u'id'])

    mo_meta = MoMeta("EquipmentPsuStatsHist", "equipmentPsuStatsHist", "[id]", VersionMeta.Version111j, "OutputOnly", 0xfL, [], ["read-only"], [u'equipmentPsuStats'], [], ["Get"])

    prop_meta = {
        "psu_i2_c_errors": MoPropertyMeta("psu_i2_c_errors", "PsuI2CErrors", "ulong", VersionMeta.Version226a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "psu_i2_c_errors_delta": MoPropertyMeta("psu_i2_c_errors_delta", "PsuI2CErrorsDelta", "ulong", VersionMeta.Version226a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "psu_i2_c_errors_delta_avg": MoPropertyMeta("psu_i2_c_errors_delta_avg", "PsuI2CErrorsDeltaAvg", "ulong", VersionMeta.Version226a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "psu_i2_c_errors_delta_max": MoPropertyMeta("psu_i2_c_errors_delta_max", "PsuI2CErrorsDeltaMax", "ulong", VersionMeta.Version226a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "psu_i2_c_errors_delta_min": MoPropertyMeta("psu_i2_c_errors_delta_min", "PsuI2CErrorsDeltaMin", "ulong", VersionMeta.Version226a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "ambient_temp": MoPropertyMeta("ambient_temp", "ambientTemp", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, ["not-applicable"], ["0-4294967295"]), 
        "ambient_temp_avg": MoPropertyMeta("ambient_temp_avg", "ambientTempAvg", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, ["not-applicable"], ["0-4294967295"]), 
        "ambient_temp_max": MoPropertyMeta("ambient_temp_max", "ambientTempMax", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, ["not-applicable"], ["0-4294967295"]), 
        "ambient_temp_min": MoPropertyMeta("ambient_temp_min", "ambientTempMin", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, ["not-applicable"], ["0-4294967295"]), 
        "child_action": MoPropertyMeta("child_action", "childAction", "string", VersionMeta.Version111j, MoPropertyMeta.INTERNAL, None, None, None, r"""((deleteAll|ignore|deleteNonPresent),){0,2}(deleteAll|ignore|deleteNonPresent){0,1}""", [], []), 
        "dn": MoPropertyMeta("dn", "dn", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, 0x2L, 0, 256, None, [], []), 
        "id": MoPropertyMeta("id", "id", "ulong", VersionMeta.Version111j, MoPropertyMeta.NAMING, None, None, None, None, [], []), 
        "input210v": MoPropertyMeta("input210v", "input210v", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "input210v_avg": MoPropertyMeta("input210v_avg", "input210vAvg", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "input210v_max": MoPropertyMeta("input210v_max", "input210vMax", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "input210v_min": MoPropertyMeta("input210v_min", "input210vMin", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "input_power": MoPropertyMeta("input_power", "inputPower", "float", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "input_power_avg": MoPropertyMeta("input_power_avg", "inputPowerAvg", "float", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "input_power_max": MoPropertyMeta("input_power_max", "inputPowerMax", "float", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "input_power_min": MoPropertyMeta("input_power_min", "inputPowerMin", "float", VersionMeta.Version251a, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "most_recent": MoPropertyMeta("most_recent", "mostRecent", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, ["false", "no", "true", "yes"], []), 
        "output12v": MoPropertyMeta("output12v", "output12v", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output12v_avg": MoPropertyMeta("output12v_avg", "output12vAvg", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output12v_max": MoPropertyMeta("output12v_max", "output12vMax", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output12v_min": MoPropertyMeta("output12v_min", "output12vMin", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output3v3": MoPropertyMeta("output3v3", "output3v3", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output3v3_avg": MoPropertyMeta("output3v3_avg", "output3v3Avg", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output3v3_max": MoPropertyMeta("output3v3_max", "output3v3Max", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output3v3_min": MoPropertyMeta("output3v3_min", "output3v3Min", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_current": MoPropertyMeta("output_current", "outputCurrent", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_current_avg": MoPropertyMeta("output_current_avg", "outputCurrentAvg", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_current_max": MoPropertyMeta("output_current_max", "outputCurrentMax", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_current_min": MoPropertyMeta("output_current_min", "outputCurrentMin", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_power": MoPropertyMeta("output_power", "outputPower", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_power_avg": MoPropertyMeta("output_power_avg", "outputPowerAvg", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_power_max": MoPropertyMeta("output_power_max", "outputPowerMax", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "output_power_min": MoPropertyMeta("output_power_min", "outputPowerMin", "float", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "rn": MoPropertyMeta("rn", "rn", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, 0x4L, 0, 256, None, [], []), 
        "sacl": MoPropertyMeta("sacl", "sacl", "string", VersionMeta.Version302c, MoPropertyMeta.READ_ONLY, None, None, None, r"""((none|del|mod|addchild|cascade),){0,4}(none|del|mod|addchild|cascade){0,1}""", [], []), 
        "status": MoPropertyMeta("status", "status", "string", VersionMeta.Version111j, MoPropertyMeta.READ_WRITE, 0x8L, None, None, r"""((removed|created|modified|deleted),){0,3}(removed|created|modified|deleted){0,1}""", [], []), 
        "suspect": MoPropertyMeta("suspect", "suspect", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, ["false", "no", "true", "yes"], []), 
        "thresholded": MoPropertyMeta("thresholded", "thresholded", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, None, [], []), 
        "time_collected": MoPropertyMeta("time_collected", "timeCollected", "string", VersionMeta.Version111j, MoPropertyMeta.READ_ONLY, None, None, None, r"""([0-9]){4}-([0-9]){2}-([0-9]){2}T([0-9]){2}:([0-9]){2}:([0-9]){2}((\.([0-9]){3})){0,1}""", [], []), 
    }

    prop_map = {
        "PsuI2CErrors": "psu_i2_c_errors", 
        "PsuI2CErrorsDelta": "psu_i2_c_errors_delta", 
        "PsuI2CErrorsDeltaAvg": "psu_i2_c_errors_delta_avg", 
        "PsuI2CErrorsDeltaMax": "psu_i2_c_errors_delta_max", 
        "PsuI2CErrorsDeltaMin": "psu_i2_c_errors_delta_min", 
        "ambientTemp": "ambient_temp", 
        "ambientTempAvg": "ambient_temp_avg", 
        "ambientTempMax": "ambient_temp_max", 
        "ambientTempMin": "ambient_temp_min", 
        "childAction": "child_action", 
        "dn": "dn", 
        "id": "id", 
        "input210v": "input210v", 
        "input210vAvg": "input210v_avg", 
        "input210vMax": "input210v_max", 
        "input210vMin": "input210v_min", 
        "inputPower": "input_power", 
        "inputPowerAvg": "input_power_avg", 
        "inputPowerMax": "input_power_max", 
        "inputPowerMin": "input_power_min", 
        "mostRecent": "most_recent", 
        "output12v": "output12v", 
        "output12vAvg": "output12v_avg", 
        "output12vMax": "output12v_max", 
        "output12vMin": "output12v_min", 
        "output3v3": "output3v3", 
        "output3v3Avg": "output3v3_avg", 
        "output3v3Max": "output3v3_max", 
        "output3v3Min": "output3v3_min", 
        "outputCurrent": "output_current", 
        "outputCurrentAvg": "output_current_avg", 
        "outputCurrentMax": "output_current_max", 
        "outputCurrentMin": "output_current_min", 
        "outputPower": "output_power", 
        "outputPowerAvg": "output_power_avg", 
        "outputPowerMax": "output_power_max", 
        "outputPowerMin": "output_power_min", 
        "rn": "rn", 
        "sacl": "sacl", 
        "status": "status", 
        "suspect": "suspect", 
        "thresholded": "thresholded", 
        "timeCollected": "time_collected", 
    }

    def __init__(self, parent_mo_or_dn, id, **kwargs):
        self._dirty_mask = 0
        self.id = id
        self.psu_i2_c_errors = None
        self.psu_i2_c_errors_delta = None
        self.psu_i2_c_errors_delta_avg = None
        self.psu_i2_c_errors_delta_max = None
        self.psu_i2_c_errors_delta_min = None
        self.ambient_temp = None
        self.ambient_temp_avg = None
        self.ambient_temp_max = None
        self.ambient_temp_min = None
        self.child_action = None
        self.input210v = None
        self.input210v_avg = None
        self.input210v_max = None
        self.input210v_min = None
        self.input_power = None
        self.input_power_avg = None
        self.input_power_max = None
        self.input_power_min = None
        self.most_recent = None
        self.output12v = None
        self.output12v_avg = None
        self.output12v_max = None
        self.output12v_min = None
        self.output3v3 = None
        self.output3v3_avg = None
        self.output3v3_max = None
        self.output3v3_min = None
        self.output_current = None
        self.output_current_avg = None
        self.output_current_max = None
        self.output_current_min = None
        self.output_power = None
        self.output_power_avg = None
        self.output_power_max = None
        self.output_power_min = None
        self.sacl = None
        self.status = None
        self.suspect = None
        self.thresholded = None
        self.time_collected = None

        ManagedObject.__init__(self, "EquipmentPsuStatsHist", parent_mo_or_dn, **kwargs)

