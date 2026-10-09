#!/usr/bin/env python3
"""
Local dev server for dist/.

Identical to `python3 -m http.server` except it sends no-store, so an edited
stylesheet or script is never served from the browser cache. Without this a
CSS change can appear to have no effect, which is a genuinely confusing way
to lose ten minutes.
"""

import sys
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler


class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        # Keep the console readable: report problems, not every 200.
        if args and str(args[1]).startswith(("4", "5")):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4321
    directory = sys.argv[2] if len(sys.argv) > 2 else "dist"
    handler = partial(NoCacheHandler, directory=directory)
    print("serving %s/ on http://localhost:%d (no-cache)" % (directory, port))
    try:
        HTTPServer(("", port), handler).serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
