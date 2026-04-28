"""Dismiss COMSOL's 'connect to server' login dialog.

Cortex pops "连接到 COMSOL Multiphysics Server" on every fresh launch.
The backend is already connected via JPype by the time the agent gets
control, so clicking "确定" (OK) is the only blocking step.

Paste into ``sim exec`` right after ``sim connect --solver comsol
--ui-mode gui``. Safe to re-run — if the dialog isn't visible the
find() simply returns None.
"""

dlg = gui.find(title_contains="连接到", timeout_s=5)
if dlg is None:
    # English-locale COMSOL uses 'Connect to COMSOL'
    dlg = gui.find(title_contains="Connect to COMSOL", timeout_s=2)

if dlg is None:
    _result = {"ok": True, "dismissed": False, "reason": "no login dialog visible"}
else:
    click_result = dlg.click("确定")
    if not click_result.get("ok"):
        click_result = dlg.click("OK")
    _result = {"ok": click_result.get("ok", False),
               "dismissed": True,
               "title": dlg.title,
               "click": click_result}
