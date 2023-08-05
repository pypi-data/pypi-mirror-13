"""This module contains the meta information of ConfigRenewResolveContext ExternalMethod."""
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ucscoremeta import MethodMeta, MethodPropertyMeta
sys.path.remove(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

method_meta = MethodMeta("ConfigRenewResolveContext", "configRenewResolveContext", "Version142b")

prop_meta = {
    "cookie": MethodPropertyMeta("Cookie", "cookie", "Xs:string", "Version142b", "InputOutput", False),
    "in_context": MethodPropertyMeta("InContext", "inContext", "Xs:unsignedLong", "Version142b", "Input", False),
    "out_context": MethodPropertyMeta("OutContext", "outContext", "Xs:unsignedLong", "Version142b", "Output", False),
}

prop_map = {
    "cookie": "cookie",
    "inContext": "in_context",
    "outContext": "out_context",
}

