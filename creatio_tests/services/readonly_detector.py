from typing import Optional, Tuple
from selenium.webdriver.remote.webelement import WebElement


class ReadonlyDetector:
    def __init__(self):
        pass

    def check(self, container: WebElement) -> Tuple[bool, str]:
        drv = container.parent
        state = drv.execute_script(
            """
var host = arguments[0];
function val(x){ return x == null ? null : String(x); }
var res = {
  hostReadonly: val(host.getAttribute('readonly')),
  hostDisabled: val(host.getAttribute('disabled')),
  hasLockIcon: !!host.querySelector('.readonly-icon,[data-mat-icon-name="lock"],[title*="Non-editable"]'),
  inputs: []
};
var nodes = host.querySelectorAll('input,textarea,select,[role="combobox"]');
nodes.forEach(function(n){
  res.inputs.push({
    readonlyAttr: val(n.getAttribute('readonly')),
    disabledAttr: val(n.getAttribute('disabled')),
    ariaReadonly: val(n.getAttribute('aria-readonly')),
    ariaDisabled: val(n.getAttribute('aria-disabled')),
    readOnlyProp: !!n.readOnly,
    disabledProp: !!n.disabled
  });
});
return res;
""",
            container,
        )
        def t(v: Optional[str]) -> bool:
            if v is None:
                return False
            s = str(v).strip().lower()
            return s in ("", "true", "1", "readonly")
        def f(v: Optional[str]) -> bool:
            return (v is not None) and (str(v).strip().lower() == "false")
        host_ro_true = t(state.get("hostReadonly"))
        host_ro_false = f(state.get("hostReadonly"))
        host_dis_true = t(state.get("hostDisabled"))
        has_icon = bool(state.get("hasLockIcon"))
        inp_ro_true = False
        inp_dis_true = False
        inp_aria_ro_true = False
        inp_aria_dis_true = False
        inp_props_ro = False
        inp_props_dis = False
        for i in state.get("inputs", []):
            if t(i.get("readonlyAttr")):
                inp_ro_true = True
            if t(i.get("disabledAttr")):
                inp_dis_true = True
            if (i.get("ariaReadonly") or "").strip().lower() == "true":
                inp_aria_ro_true = True
            if (i.get("ariaDisabled") or "").strip().lower() == "true":
                inp_aria_dis_true = True
            if bool(i.get("readOnlyProp")):
                inp_props_ro = True
            if bool(i.get("disabledProp")):
                inp_props_dis = True
        any_ro = has_icon or host_ro_true or host_dis_true or inp_ro_true or inp_dis_true or inp_aria_ro_true or inp_aria_dis_true or inp_props_ro or inp_props_dis
        if host_ro_false and not any_ro:
            return False, "editable (host readonly='false')"
        if any_ro:
            reasons = []
            if has_icon: reasons.append("lock icon")
            if host_ro_true: reasons.append("host readonly")
            if host_dis_true: reasons.append("host disabled")
            if inp_ro_true: reasons.append("input readonly attr")
            if inp_dis_true: reasons.append("input disabled attr")
            if inp_aria_ro_true: reasons.append("aria-readonly=true")
            if inp_aria_dis_true: reasons.append("aria-disabled=true")
            if inp_props_ro: reasons.append("input.readOnly")
            if inp_props_dis: reasons.append("input.disabled")
            return True, ", ".join(reasons) if reasons else "readonly signals"
        return False, "no readonly signals"
