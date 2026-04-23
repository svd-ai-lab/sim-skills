"""Fill Fluent's 'Save Case As' file-save dialog.

``session.file.write_case(path, overwrite=True)`` is usually preferred.
Fall back to this only if the API path is unavailable (older Fluent
builds, non-SDK workflows, or when you're driving the menu manually
for a demo).

Expects an already-open standard Windows file-save dialog — Fluent
opens one via File > Write > Case... and the modal's title contains
"Select File". Fill the path, click OK.
"""

TARGET = r"C:\work\out.cas.h5"

dlg = gui.find(title_contains="Select File", timeout_s=5)
if dlg is None:
    _result = {"ok": False, "error": "Select File dialog not visible"}
else:
    send = dlg.send_text(TARGET, into="File name")
    click = dlg.click("Save") if send.get("ok") else {"ok": False, "skipped": True}
    if not click.get("ok"):
        click = dlg.click("OK")
    _result = {"ok": click.get("ok", False), "send": send, "click": click}
