"""Console configuration for pipeline entry points."""

from __future__ import annotations

import sys


def configure_console() -> None:
    """Make stdout and stderr tolerant of non-ASCII progress output.

    Module logs contain characters such as the date-range arrow in the RKEG data
    window message. On a console using a legacy code page (the Windows default)
    writing them raises ``UnicodeEncodeError``, which aborts an otherwise
    successful run part way through reporting progress and can leave a run
    without its manifest. Reconfiguring to UTF-8 with replacement makes logging
    lossy at worst rather than fatal.

    Safe to call more than once, and a no-op on streams that cannot be
    reconfigured (for example when stdout has been replaced by a plain object).
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue
