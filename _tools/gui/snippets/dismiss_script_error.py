"""Dismiss Mechanical's 'Script Error' dialog.

Mechanical (ACT/IronPython surface) throws a modal 'Script Error' popup
when a posted script raises. The Python binding (PyMechanical) will be
reported success over gRPC even while this dialog holds the GUI
hostage. Poll for it after every risky exec and click OK so later
`sim screenshot` calls aren't stuck reading the popup.
"""

dlg = gui.find(title_contains="Script Error", timeout_s=2)
if dlg is None:
    _result = {"ok": True, "dismissed": False}
else:
    before = dlg.screenshot(label="script_error_before_dismiss")
    click = dlg.click("OK")
    _result = {"ok": click.get("ok", False),
               "dismissed": True,
               "title": dlg.title,
               "screenshot": before.get("path"),
               "click": click}
