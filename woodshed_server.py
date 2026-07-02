#!/usr/bin/env python3
"""
woodshed_server.py — The Woodshed local server + save bridge (wood-7).

WHAT THIS IS
------------
A tiny, stdlib-only (no pip) drop-in replacement for `python3 -m http.server`.
It does TWO jobs:

  1. Serves the Trumpet folder statically on port 8420 (same as the old
     launcher), so the no-build vanilla-JS app still loads at
     http://localhost:8420/ exactly as before.

  2. Exposes three same-origin POST endpoints so the app can WRITE files to
     this folder directly (no Blob-download / manual export). This is the
     server side of the wood-9 feedback loop + wood-15 nightly agent:

       POST /save-day       -> writes the request body to  logs/<date>.md
                               (date = today YYYY-MM-DD, or a "date" field
                                supplied in a JSON request — see below)
       POST /save-brain     -> writes the request body to  mission-control.json
                               and then regenerates public-assets/snapshot.json
                               from the just-saved state (M4 publish heartbeat;
                               regen failures never fail the brain save)
       POST /save-feedback  -> APPENDS one newline-terminated JSON line to
                               feedback.jsonl

   All writes are confined to this folder; path traversal is rejected.
   Endpoints return JSON {"ok":true,"path":...} on success and a 4xx with
   {"ok":false,"error":...} on bad input. CORS is permissive but the page is
   served same-origin so it Just Works with a plain fetch().

REQUEST FORMATS
---------------
The endpoints are deliberately forgiving — they persist what the page sends:

  * Raw body (Content-Type text/plain, application/json, application/x-ndjson,
    text/markdown): the body IS the content to write/append.

  * JSON envelope {"content": "...", "date": "YYYY-MM-DD"} (optional): if the
    body parses as a JSON object that has a "content" key, that string is the
    content and an optional "date" key overrides the filename date for
    /save-day. This lets the page pin a date without juggling Content-Type.

For /save-brain the body is written verbatim as mission-control.json (the page
is expected to send JSON that matches mission-control.schema.json; this server
does NOT validate the schema — it just persists what the app produces, exactly
like the old export, and notes that in the contract).

HOW THE LAUNCHER USES IT
------------------------
"Start Woodshed.command" currently runs:  python3 -m http.server $PORT
To use this bridge instead, that one line becomes:
    python3 "$(dirname "$0")/woodshed_server.py" $PORT
(Port defaults to 8420 if omitted.) The launcher swap is intentionally NOT
applied automatically — see the wood-7 report's [confirm: apply launcher swap].

Stdlib only. Python 3.6+. Runs on a plain macOS python3.
"""

import json
import os
import re
import sys
import datetime
import subprocess
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# The folder we serve and write into = the folder this script lives in.
ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PORT = 8420
MAX_BODY = 16 * 1024 * 1024  # 16 MB safety cap on a POST body.

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _today():
    return datetime.date.today().isoformat()


def _safe_join(root, *parts):
    """Join under root and guarantee the result stays inside root.

    Returns the absolute path, or None if it would escape (path traversal).
    """
    target = os.path.abspath(os.path.join(root, *parts))
    root_abs = os.path.abspath(root)
    # Ensure target is root itself or strictly within root.
    if target == root_abs:
        return None
    if os.path.commonpath([root_abs, target]) != root_abs:
        return None
    return target


class WoodshedHandler(SimpleHTTPRequestHandler):
    """Static file server (inherited) + three POST save endpoints."""

    server_version = "Woodshed/1.0"

    # ---- helpers ---------------------------------------------------------
    def _send_json(self, status, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # Permissive CORS (page is same-origin, but harmless and future-proof).
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        """Return (content_str, parsed_json_or_None) or (None, None) on error."""
        try:
            length = int(self.headers.get("Content-Length", 0))
        except (TypeError, ValueError):
            length = 0
        if length < 0 or length > MAX_BODY:
            return None, None
        raw = self.rfile.read(length) if length else b""
        text = raw.decode("utf-8", errors="replace")
        parsed = None
        stripped = text.strip()
        if stripped[:1] in ("{", "["):
            try:
                parsed = json.loads(stripped)
            except ValueError:
                parsed = None
        return text, parsed

    @staticmethod
    def _extract(text, parsed):
        """Resolve (content, date_override, date_bad) from a raw body or {content,date} envelope.

        date_override is the validated YYYY-MM-DD or None (no date supplied).
        date_bad is True when a "date" key was present but malformed, so the
        caller can reject it instead of silently writing to today.
        """
        date_override = None
        date_bad = False
        content = text
        if isinstance(parsed, dict) and "content" in parsed:
            c = parsed.get("content")
            content = c if isinstance(c, str) else json.dumps(c)
            if "date" in parsed:
                d = parsed.get("date")
                if isinstance(d, str) and _DATE_RE.match(d.strip()):
                    date_override = d.strip()
                else:
                    date_bad = True
        return content, date_override, date_bad

    # ---- CORS preflight --------------------------------------------------
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # ---- POST router -----------------------------------------------------
    def do_POST(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        if path == "/save-day":
            return self._save_day()
        if path == "/save-brain":
            return self._save_brain()
        if path == "/save-feedback":
            return self._save_feedback()
        # --- transcription pipeline (drives the Mac homr loop from the browser) ---
        if path == "/transcribe/cut":
            return self._transcribe_cut()
        if path == "/transcribe/homr":
            return self._transcribe_homr()
        if path == "/transcribe/save-chart":
            return self._transcribe_save_chart()
        self._send_json(404, {"ok": False, "error": "unknown endpoint: " + path})

    # ====================================================================
    #  TRANSCRIPTION PIPELINE  (transcribe.html → these endpoints)
    #
    #  The Woodshed transcription flow is: pick a Real Book tune → cut the
    #  page into per-line strips (cut_lines.py) → run homr on each strip
    #  (.venv-homr/bin/homr, on Chris's Mac) → assemble + correct in the
    #  browser → save the finished head into charts/user-heads.json so the
    #  Tune Vault renders it in place of the Real Book scan.
    #
    #  homr is AGPL/offline — it only ever runs here, on the local machine,
    #  producing DATA (MusicXML/ABC). It is never shipped in the app.
    # ====================================================================

    # Where cut/homr scratch work lives (served statically under root, so the
    # browser can show the strip PNGs by URL).
    _TX_BASE = os.path.join("pipelines", "score-engine", "experiments")
    _TX_CUT = os.path.join("pipelines", "tools", "cut_lines.py")
    _TX_HOMR = os.path.join(
        "pipelines", "score-engine", "experiments", ".venv-homr", "bin", "homr"
    )

    def _tx_dir(self, slug):
        """Resolve the scratch dir for a tune slug, guarded under _TX_BASE."""
        slug = re.sub(r"[^a-z0-9\-]", "", (slug or "").lower())
        if not slug:
            return None
        d = _safe_join(ROOT, self._TX_BASE, slug + "-auto")
        return d

    def _transcribe_cut(self):
        """Render a Real Book page and slice it into per-line strips.

        Body JSON: {"slug": "<tune-id>", "page": <printedPage int>}
        Returns {ok, dir, strips:[{line, url}], contact}.
        """
        _, parsed = self._read_body()
        if not isinstance(parsed, dict):
            return self._send_json(400, {"ok": False, "error": "expected JSON {slug, page}"})
        slug = parsed.get("slug")
        page = parsed.get("page")
        try:
            page = int(page)
        except (TypeError, ValueError):
            return self._send_json(400, {"ok": False, "error": "page must be an integer"})
        outdir = self._tx_dir(slug)
        if outdir is None:
            return self._send_json(400, {"ok": False, "error": "bad slug"})
        cut = os.path.join(ROOT, self._TX_CUT)
        if not os.path.isfile(cut):
            return self._send_json(500, {"ok": False, "error": "cut_lines.py not found"})
        os.makedirs(outdir, exist_ok=True)
        try:
            proc = subprocess.run(
                [sys.executable, cut, str(page), outdir],
                capture_output=True, text=True, timeout=180, cwd=ROOT,
            )
        except subprocess.TimeoutExpired:
            return self._send_json(504, {"ok": False, "error": "cut_lines.py timed out"})
        except Exception as exc:
            return self._send_json(500, {"ok": False, "error": "cut failed: " + str(exc)})
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()
            return self._send_json(500, {
                "ok": False,
                "error": "cut_lines.py exit %d: %s" % (
                    proc.returncode, tail[-1] if tail else "unknown"),
            })
        strips_dir = os.path.join(outdir, "strips")
        strips = []
        if os.path.isdir(strips_dir):
            for f in sorted(os.listdir(strips_dir)):
                m = re.match(r"line-(\d+)\.png$", f)
                if m:
                    rel = os.path.relpath(os.path.join(strips_dir, f), ROOT)
                    strips.append({"line": int(m.group(1)),
                                   "url": "/" + rel.replace(os.sep, "/")})
        contact = None
        for f in os.listdir(outdir):
            if f.endswith("-lines.png"):
                rel = os.path.relpath(os.path.join(outdir, f), ROOT)
                contact = "/" + rel.replace(os.sep, "/")
                break
        self._send_json(200, {
            "ok": True,
            "dir": os.path.relpath(outdir, ROOT).replace(os.sep, "/"),
            "strips": strips,
            "contact": contact,
        })

    def _transcribe_homr(self):
        """Run homr on the selected strips and return their MusicXML.

        Body JSON: {"dir": "<relpath under experiments>", "lines": [int,...]}
        (lines optional — omit to run every strip). Returns
        {ok, results:[{line, xml|error}]}.
        """
        _, parsed = self._read_body()
        if not isinstance(parsed, dict):
            return self._send_json(400, {"ok": False, "error": "expected JSON {dir, lines}"})
        rel = parsed.get("dir") or ""
        outdir = _safe_join(ROOT, rel)
        base = os.path.abspath(os.path.join(ROOT, self._TX_BASE))
        if outdir is None or os.path.commonpath([base, outdir]) != base:
            return self._send_json(400, {"ok": False, "error": "dir outside transcribe scratch"})
        strips_dir = os.path.join(outdir, "strips")
        if not os.path.isdir(strips_dir):
            return self._send_json(404, {"ok": False, "error": "no strips/ in dir (run cut first)"})
        homr = os.path.join(ROOT, self._TX_HOMR)
        if not os.path.isfile(homr):
            return self._send_json(500, {
                "ok": False,
                "error": "homr not found (.venv-homr missing — reinstall on the Mac)",
            })
        want = parsed.get("lines")
        want = set(int(x) for x in want) if isinstance(want, list) else None
        results = []
        for f in sorted(os.listdir(strips_dir)):
            m = re.match(r"line-(\d+)\.png$", f)
            if not m:
                continue
            line = int(m.group(1))
            if want is not None and line not in want:
                continue
            img = os.path.join(strips_dir, f)
            xml_path = img[:-4] + ".musicxml"
            try:
                proc = subprocess.run(
                    [homr, img], capture_output=True, text=True, timeout=300, cwd=ROOT,
                )
            except Exception as exc:
                results.append({"line": line, "error": "homr failed: " + str(exc)})
                continue
            if proc.returncode != 0 or not os.path.isfile(xml_path):
                tail = (proc.stderr or proc.stdout or "").strip().splitlines()
                results.append({"line": line,
                                "error": tail[-1] if tail else "homr produced no MusicXML"})
                continue
            with open(xml_path, "r", encoding="utf-8") as fh:
                results.append({"line": line, "xml": fh.read()})
        self._send_json(200, {"ok": True, "results": results})

    def _transcribe_save_chart(self):
        """Persist a finished head into charts/user-heads.json (+ .js mirror).

        Body JSON = one USER_CHART entry {id, forTune, title, source, key,
        style, bpm, abc, bars}. Replace-by-forTune (newest wins). The .js
        mirror is what index.html loads at boot.
        """
        _, parsed = self._read_body()
        if not isinstance(parsed, dict) or not parsed.get("abc"):
            return self._send_json(400, {"ok": False, "error": "expected a chart entry with abc"})
        for_tune = parsed.get("forTune") or parsed.get("title")
        if not for_tune:
            return self._send_json(400, {"ok": False, "error": "entry needs forTune or title"})
        charts_dir = _safe_join(ROOT, "charts")
        if charts_dir is None:
            return self._send_json(400, {"ok": False, "error": "path traversal rejected"})
        os.makedirs(charts_dir, exist_ok=True)
        json_path = os.path.join(charts_dir, "user-heads.json")
        arr = []
        if os.path.isfile(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                if isinstance(loaded, list):
                    arr = loaded
            except (ValueError, OSError):
                arr = []
        norm = lambda s: re.sub(r"[^a-z0-9]", "", str(s or "").lower())
        key = norm(for_tune)
        arr = [c for c in arr if norm(c.get("forTune") or c.get("title")) != key]
        arr.append(parsed)
        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(arr, fh, ensure_ascii=False, indent=1)
        # JS mirror loaded by index.html (json.dumps output is valid JS).
        js_path = os.path.join(charts_dir, "user-heads.js")
        with open(js_path, "w", encoding="utf-8") as fh:
            fh.write("/* Generated by woodshed_server.py (transcribe.html saves). "
                     "Canonical source: user-heads.json. Do not hand-edit. */\n")
            fh.write("window.USER_HEADS=" + json.dumps(arr, ensure_ascii=False) + ";\n")
        self._send_json(200, {
            "ok": True,
            "forTune": for_tune,
            "count": len(arr),
            "path": "charts/user-heads.json",
        })

    def _save_day(self):
        text, parsed = self._read_body()
        if text is None:
            return self._send_json(413, {"ok": False, "error": "body missing or too large"})
        content, date_override, date_bad = self._extract(text, parsed)
        if date_bad:
            return self._send_json(400, {"ok": False, "error": "bad date (expected YYYY-MM-DD)"})
        date = date_override or _today()
        if not _DATE_RE.match(date):
            return self._send_json(400, {"ok": False, "error": "bad date: " + str(date)})
        logs_dir = _safe_join(ROOT, "logs")
        if logs_dir is None:
            return self._send_json(400, {"ok": False, "error": "path traversal rejected"})
        os.makedirs(logs_dir, exist_ok=True)
        target = _safe_join(ROOT, "logs", date + ".md")
        if target is None:
            return self._send_json(400, {"ok": False, "error": "path traversal rejected"})
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        self._send_json(200, {"ok": True, "path": os.path.relpath(target, ROOT)})

    @staticmethod
    def _regen_snapshot():
        """Regenerate public-assets/snapshot.json from the just-saved brain.

        Runs the existing wood-43 generator (render_snapshot.py) as a subprocess
        so the M4 public heartbeat (wood-46/47/48) always reflects the real
        practice state with no manual step. This is best-effort and MUST NOT be
        able to fail the brain save: every failure mode (missing script, error,
        non-zero exit, timeout) is caught and reported as a sub-result, never
        raised. Returns a small JSON-able dict describing the outcome.
        """
        script = os.path.join(ROOT, "public-assets", "render_snapshot.py")
        if not os.path.isfile(script):
            return {"ok": False, "error": "render_snapshot.py not found"}
        try:
            proc = subprocess.run(
                [sys.executable, script],
                capture_output=True, text=True, timeout=30, cwd=ROOT,
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "render_snapshot.py timed out"}
        except Exception as exc:  # never let regen break the brain save
            return {"ok": False, "error": "regen failed: " + str(exc)}
        if proc.returncode != 0:
            # Surface a short reason; keep the full stderr off the wire.
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()
            reason = tail[-1] if tail else ("exit %d" % proc.returncode)
            return {"ok": False, "error": "render_snapshot.py exit %d: %s"
                    % (proc.returncode, reason)}
        return {"ok": True, "path": os.path.join("public-assets", "snapshot.json")}

    def _save_brain(self):
        text, parsed = self._read_body()
        if text is None:
            return self._send_json(413, {"ok": False, "error": "body missing or too large"})
        content, _, _ = self._extract(text, parsed)
        # Persist verbatim as mission-control.json. We do NOT validate against
        # mission-control.schema.json here — the server just stores what the
        # app produced (same contract as the old Blob export).
        target = _safe_join(ROOT, "mission-control.json")
        if target is None:
            return self._send_json(400, {"ok": False, "error": "path traversal rejected"})
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        # After a successful brain save, regenerate the public snapshot from the
        # now-current state (M4 publish heartbeat). Best-effort: the brain save
        # is already done and reported ok regardless of the regen outcome.
        snapshot_result = self._regen_snapshot()
        self._send_json(200, {
            "ok": True,
            "path": os.path.relpath(target, ROOT),
            "snapshot": snapshot_result,
        })

    def _save_feedback(self):
        text, parsed = self._read_body()
        if text is None:
            return self._send_json(413, {"ok": False, "error": "body missing or too large"})
        content, _, _ = self._extract(text, parsed)
        line = content.strip("\n")
        if not line.strip():
            return self._send_json(400, {"ok": False, "error": "empty feedback line"})
        if "\n" in line:
            return self._send_json(400, {"ok": False, "error": "feedback must be a single JSON line"})
        target = _safe_join(ROOT, "feedback.jsonl")
        if target is None:
            return self._send_json(400, {"ok": False, "error": "path traversal rejected"})
        with open(target, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        self._send_json(200, {"ok": True, "path": os.path.relpath(target, ROOT)})

    # Quieter logging (one line per request, no noise).
    def log_message(self, fmt, *args):
        sys.stderr.write("[woodshed] %s - %s\n" % (self.address_string(), fmt % args))


def main():
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            sys.stderr.write("Usage: woodshed_server.py [PORT]\n")
            sys.exit(2)
    handler = partial(WoodshedHandler, directory=ROOT)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    sys.stderr.write(
        "[woodshed] serving %s at http://localhost:%d/  "
        "(POST /save-day /save-brain /save-feedback)\n" % (ROOT, port)
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    main()
