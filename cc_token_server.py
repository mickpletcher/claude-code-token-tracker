"""
Claude Code Token Server
Reads ~/.claude/projects/**/*.jsonl and serves live usage data to the tracker HTML.
Usage: python cc_token_server.py
Then open http://localhost:7823 in your browser.
"""

import json
import os
import glob
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

PORT = 7823
CLAUDE_DIR = Path.home() / ".claude" / "projects"


def read_usage():
    sessions = []
    pattern = str(CLAUDE_DIR / "**" / "*.jsonl")
    files = glob.glob(pattern, recursive=True)

    for filepath in sorted(files):
        project_name = Path(filepath).parent.name  # folder name = hashed project path
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            continue

        # Each JSONL file = one Claude Code session
        session_input = 0
        session_output = 0
        session_cache_write = 0
        session_cache_read = 0
        session_ts = None
        message_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Grab timestamp from first entry
            if session_ts is None:
                ts_raw = entry.get("timestamp") or entry.get("ts")
                if ts_raw:
                    try:
                        session_ts = ts_raw
                    except Exception:
                        pass

            # Usage lives inside assistant message entries
            msg = entry.get("message", {})
            usage = msg.get("usage", {})

            if usage:
                session_input       += usage.get("input_tokens", 0)
                session_output      += usage.get("output_tokens", 0)
                session_cache_write += usage.get("cache_creation_input_tokens", 0)
                session_cache_read  += usage.get("cache_read_input_tokens", 0)
                message_count       += 1

        if session_input + session_output + session_cache_write + session_cache_read == 0:
            continue

        # Try to get a human-readable project path from the mapping file
        display_name = project_name
        mapping_file = Path.home() / ".claude" / "projects" / project_name / "project.json"
        if mapping_file.exists():
            try:
                with open(mapping_file) as mf:
                    meta = json.load(mf)
                    display_name = meta.get("path", project_name).split("/")[-1] or project_name
            except Exception:
                pass

        sessions.append({
            "ts": session_ts or datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
            "file": filepath,
            "project": display_name,
            "input": session_input,
            "output": session_output,
            "cacheWrite": session_cache_write,
            "cacheRead": session_cache_read,
            "messages": message_count,
        })

    # Sort newest first
    sessions.sort(key=lambda s: s["ts"], reverse=True)
    return sessions


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/usage":
            self._serve_json()
        elif self.path in ("/", "/index.html"):
            self._serve_file("claude-code-token-tracker.html", "text/html")
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_json(self):
        try:
            data = read_usage()
            body = json.dumps({"sessions": data, "generated": datetime.now().isoformat()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    def _serve_file(self, filename, mime):
        path = Path(__file__).parent / filename
        if not path.exists():
            self.send_response(404)
            self.end_headers()
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # suppress request noise


if __name__ == "__main__":
    if not CLAUDE_DIR.exists():
        print(f"[warn] Claude Code data directory not found: {CLAUDE_DIR}")
        print("       Make sure Claude Code has been run at least once.")

    print(f"Claude Code Token Server running at http://localhost:{PORT}")
    print(f"Reading sessions from: {CLAUDE_DIR}")
    print("Press Ctrl+C to stop.\n")

    server = HTTPServer(("localhost", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
