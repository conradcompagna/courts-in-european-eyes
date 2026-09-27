"""Serve the embassy explorer and collect classroom drafts in this project."""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


PROJECT_ROOT = Path(__file__).resolve().parent
MAX_REQUEST_BYTES = 2_000_000
PASSAGE_ID = re.compile(r"[a-z][a-z0-9_-]{1,79}\Z")


def make_handler(project_root: Path = PROJECT_ROOT, submissions_root: Path | None = None):
    """Build a handler with a private submissions directory."""
    project_root = project_root.resolve()
    submissions_root = (submissions_root or project_root / "submissions").resolve()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(project_root), **kwargs)

        def _public_path(self) -> str:
            return posixpath.normpath(unquote(urlsplit(self.path).path))

        def _serve_public(self, head: bool = False):
            path = self._public_path()
            if path == "/":
                self.send_response(302)
                self.send_header("Location", "/explorer/")
                self.end_headers()
            elif path == "/explorer" or path.startswith("/explorer/"):
                (super().do_HEAD if head else super().do_GET)()
            else:
                self.send_error(404, "Not found")

        def do_GET(self):
            self._serve_public()

        def do_HEAD(self):
            self._serve_public(head=True)

        def _json(self, status: int, payload: dict):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if urlsplit(self.path).path != "/api/submissions":
                self._json(404, {"error": "Unknown endpoint."})
                return
            if self.headers.get_content_type() != "application/json":
                self._json(415, {"error": "Expected JSON."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                length = 0
            if not 0 < length <= MAX_REQUEST_BYTES:
                self._json(413, {"error": "Submission is empty or too large."})
                return
            try:
                data = json.loads(self.rfile.read(length))
                record = self._validate(data)
            except (ValueError, TypeError) as error:
                self._json(400, {"error": str(error)})
                return

            now = datetime.now(timezone.utc)
            record["savedAt"] = now.isoformat(timespec="seconds")
            slug = re.sub(r"[^A-Za-z0-9_-]+", "-", record["studentId"]).strip("-")[:40] or "student"
            folder = submissions_root / ("drafts" if record["kind"] == "draft" else "completed")
            filename = f"{now:%Y%m%dT%H%M%SZ}_{slug}_{record['anchorId']}_{uuid.uuid4().hex[:8]}.json"
            try:
                folder.mkdir(parents=True, exist_ok=True)
                with (folder / filename).open("x", encoding="utf-8") as file:
                    json.dump(record, file, ensure_ascii=False, indent=2)
                    file.write("\n")
                    file.flush()
                    os.fsync(file.fileno())
            except OSError:
                self._json(500, {"error": "Could not write the submission."})
                return
            self._json(201, {"ok": True, "savedAt": record["savedAt"], "file": filename})

        @staticmethod
        def _validate(data: object) -> dict:
            if not isinstance(data, dict):
                raise ValueError("Submission must be an object.")
            kind = data.get("kind")
            if kind not in {"draft", "completed"}:
                raise ValueError("Invalid submission type.")
            student_id = data.get("studentId")
            if not isinstance(student_id, str) or not 1 <= len(student_id.strip()) <= 80:
                raise ValueError("Enter a student name or ID.")
            student_id = student_id.strip()
            if any(ord(char) < 32 for char in student_id):
                raise ValueError("Student name or ID contains control characters.")
            anchor_id = data.get("anchorId")
            passage_ids = data.get("passageIds")
            if not isinstance(anchor_id, str) or not PASSAGE_ID.fullmatch(anchor_id):
                raise ValueError("Invalid selected passage.")
            if not isinstance(passage_ids, list) or len(passage_ids) != 6 or passage_ids[0] != anchor_id:
                raise ValueError("Expected the selected passage and five neighbours.")
            if any(not isinstance(pid, str) or not PASSAGE_ID.fullmatch(pid) for pid in passage_ids):
                raise ValueError("Invalid passage ID.")
            if len(set(passage_ids)) != 6:
                raise ValueError("Passages must be distinct.")
            raw_notes = data.get("notes")
            if not isinstance(raw_notes, dict):
                raise ValueError("Expected passage summaries.")
            notes = {}
            for pid in passage_ids:
                note = raw_notes.get(pid, "")
                if not isinstance(note, str) or len(note) > 20_000:
                    raise ValueError("Invalid passage summary.")
                notes[pid] = note
            essay = data.get("essay", "")
            if not isinstance(essay, str) or len(essay) > 100_000:
                raise ValueError("Invalid synthesis.")
            counts = {pid: len(notes[pid].split()) for pid in passage_ids}
            essay_count = len(essay.split())
            if kind == "completed" and (any(count < 100 for count in counts.values()) or essay_count < 500):
                raise ValueError("Completed work needs six 100-word summaries and a 500-word synthesis.")
            return {
                "kind": kind,
                "studentId": student_id,
                "anchorId": anchor_id,
                "passageIds": passage_ids,
                "notes": notes,
                "essay": essay,
                "wordCounts": {"notes": counts, "essay": essay_count},
            }

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Bind address; use 0.0.0.0 for a trusted classroom LAN")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    handler = make_handler()
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        print(f"Explorer: http://{args.host}:{args.port}/explorer/", flush=True)
        print(f"Submissions: {PROJECT_ROOT / 'submissions'}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
