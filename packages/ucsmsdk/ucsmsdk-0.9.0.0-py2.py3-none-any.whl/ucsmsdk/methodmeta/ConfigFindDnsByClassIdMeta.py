"""This module contains the meta information of ConfigFindDnsByClassId ExternalMethod."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucscoremeta import MethodMeta, MethodPropertyMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

method_meta = MethodMeta("ConfigFindDnsByClassId", "configFindDnsByClassId", "Version142b")

prop_meta = {
    "class_id": MethodPropertyMeta("ClassId", "classId", "NamingClassId", "Version142b", "InputOutput", False),
    "cookie": MethodPropertyMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
    "in_filter": MethodPropertyMeta("InFilter", "inFilter", "FilterFilter", "Version142b", "Input", True),
    "out_dns": MethodPropertyMeta("OutDns", "outDns", "DnSet", "Version142b", "Output", True),
}

prop_map = {
    "classId": "class_id",
    "cookie": "cookie",
    "inFilter": "in_filter",
    "outDns": "out_dns",
}

