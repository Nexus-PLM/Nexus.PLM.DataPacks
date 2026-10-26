"""The toolkit every NX-200 role agent uses to work in Nexus PLM as itself.

An agent is a person with a login, not a script with an admin token. Everything here goes
through the same REST API the web client uses, authenticated as that person, so whatever
the security model forbids them is genuinely forbidden — a 403 is a finding, not an
obstacle to route around.

    from plm_agent import Agent
    me = Agent("m.sandoval")                  # logs in, prints who you are
    part = me.object("LSS-21-0012")           # a part, by part number
    me.set_attributes(part, {"massKg": 1.38})
    me.say("NX-200 ATA 21 scoop redesign", "Mass is now 1.38 kg after the lip change.")
    me.bug("Schedule", "Gantt opens on today", "...", severity="Major")

Three rules the agents are held to, enforced here rather than left to good intentions:

* **Identity is the token.** Every write is attributed by the server to the logged-in
  user. No agent can act as anyone else, and nothing here accepts an actor argument.
* **A refusal is data.** `allow_403=True` turns a permission refusal into a returned
  `Refused` rather than an exception, so an agent can probe what it may do and report it.
* **Bugs are reported, not fixed.** `bug()` appends to a shared JSONL that the PLM
  administrator collects and files on the Nexus Issues board. An agent never edits the
  product and never files its own card.
"""

from __future__ import annotations

import json
import os
import sys
import threading
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

import requests

requests.packages.urllib3.disable_warnings()

def _endpoint(var, filekey, what, example):
    """One service's address, from the environment or a git-ignored targets.json beside this file.

    No host is written into this repo. A dev-LAN address as a DEFAULT is the shape the
    no-hardcoded-endpoints rule exists to stop (NI-00000080): it works silently for whoever
    wrote it and points at a stranger's network for everyone else, and nothing says so.
    """
    value = os.environ.get(var)
    if not value:
        try:
            value = json.loads((Path(__file__).parent / "targets.json")
                               .read_text(encoding="utf-8-sig")).get(filekey)
        except FileNotFoundError:
            value = None
        except Exception as exc:
            raise SystemExit("targets.json beside plm_agent.py could not be read: %s" % exc)
    if not value:
        raise SystemExit(
            "No %s endpoint. Set %s, or copy targets.example.json to targets.json beside "
            "plm_agent.py and fill in %r (e.g. %s)." % (what, var, filekey, example))
    return str(value).rstrip("/")


ENGINE = _endpoint("NEXUS_ENGINE", "engine", "Engine", "https://your-server:5000")
VAULT = _endpoint("NEXUS_VAULT", "vault", "Vault", "https://your-server:5200")
PASSWORD = os.environ.get("NEXUS_DEMO_PASSWORD", "Nexus2025!")

# The administrator is a different matter from the nine demo logins: it can change the
# type model and every object on the site, so its password is never written down here.
# NEXUS_ADMIN_PASSWORD, or `admin_agent()` asks for it.
ADMIN_USERNAME = os.environ.get("NEXUS_ADMIN_USERNAME", "admin")

HERE = Path(__file__).parent
BUG_LOG = Path(os.environ.get("NEXUS_BUG_LOG", HERE / "reports" / "bugs.jsonl"))
ACTIVITY_LOG = Path(os.environ.get("NEXUS_ACTIVITY_LOG",
                                   HERE / "reports" / "activity.jsonl"))
_LOCK = threading.Lock()


# How long a discussion message may be. A chat message is a few sentences; the first run
# of this scenario averaged five thousand characters a message and the longest was over
# twenty thousand, which is a document posted into a conversation.
MESSAGE_LIMIT = 900

# A signed position - a disposition, a DER decision, a refusal somebody will be held to -
# earns more room. Still capped: beyond this it belongs on the object as a finding or a
# note, where it can be navigated to and where it survives the thread.
FORMAL_MESSAGE_LIMIT = 2500


def admin_agent(role: str = "PLM Administrator") -> "Agent":
    """The administrator, whose password comes from the environment or from a prompt.

    Dataset maintenance - transferring ownership, clearing a stale reference, re-deriving
    a calculated value - is done as the administrator because most of this dataset is
    Released and correctly refuses an engineer's edit. That is the same act as loading it,
    not a role doing its job, so it is deliberately a little awkward: nothing in this
    repository stores the password, and a script that wants it has to be run by somebody
    who has it.
    """
    secret = os.environ.get("NEXUS_ADMIN_PASSWORD")
    if not secret:
        # Only prompt when somebody is there to answer. Under a pipe, a scheduler or an
        # agent's shell, getpass blocks on a terminal that does not exist and the script
        # looks like it is running - a 40-minute sweep once "ran" without sending a single
        # request, waiting on this line for a password nobody could see.
        if not sys.stdin.isatty():
            raise SystemExit("No administrator password and no terminal to ask on. "
                             "Set NEXUS_ADMIN_PASSWORD and re-run.")
        import getpass
        secret = getpass.getpass(f"{ADMIN_USERNAME} password: ")
    if not secret:
        raise SystemExit("No administrator password. Set NEXUS_ADMIN_PASSWORD and re-run.")
    return Agent(ADMIN_USERNAME, password=secret, role=role)


class Refused(Exception):
    """The server refused this action. Carries the status and the server's reason."""

    def __init__(self, method, path, status, body):
        self.method, self.path, self.status, self.body = method, path, status, body
        super().__init__(f"{method} {path} -> {status} {str(body)[:300]}")


def _append(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def object_id(part_number: str) -> str:
    """The demo's deterministic object id for a part number."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL,
                          f"nexus-plm:lightjet-demo:{part_number}"))


class Agent:
    """One person, logged in, acting as themselves."""

    def __init__(self, username: str, password: str | None = None,
                 role: str | None = None):
        self.username = username
        self.role = role or username
        self.session = requests.Session()
        self.session.verify = False
        body = self.session.post(f"{ENGINE}/api/auth/login",
                                 json={"username": username,
                                       "password": password or PASSWORD},
                                 timeout=30).json()
        if not body.get("success"):
            raise RuntimeError(f"{username} could not log in: {body.get('message')}")
        self.user_id = body["userId"]
        self.display_name = body.get("displayName") or username
        self.session.headers["Authorization"] = f"Bearer {body['tokenValue']}"
        # One file per agent. Agents run as separate processes, so a shared append-only
        # file is a race however careful a single process is with its own lock.
        self.bug_log = BUG_LOG.parent / f"bugs-{username}.jsonl"
        self.activity_log = ACTIVITY_LOG.parent / f"activity-{username}.jsonl"
        self.log("login", f"signed in as {self.display_name}")

    # ── plumbing ────────────────────────────────────────────────────────────
    def _call(self, method, path, allow_403=False, base=ENGINE, **kwargs):
        response = self.session.request(method, f"{base}{path}", timeout=120, **kwargs)
        if response.status_code == 404 and method == "GET":
            return None
        if response.status_code in (401, 403) and allow_403:
            return Refused(method, path, response.status_code, response.text[:400])
        if response.status_code >= 400:
            raise Refused(method, path, response.status_code, response.text[:400])
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, path, **kw):
        return self._call("GET", path, **kw)

    def post(self, path, body=None, **kw):
        return self._call("POST", path, json=body, **kw)

    def put(self, path, body, **kw):
        return self._call("PUT", path, json=body, **kw)

    def patch(self, path, body, **kw):
        return self._call("PATCH", path, json=body, **kw)

    def delete(self, path, **kw):
        """Deletes. Present for verification probes that must clean up after themselves.

        No agent calls this during the scenario: the roles report what they cannot do
        rather than tidying the dataset, and a delete they were refused is a finding.
        It exists so a check that has to CREATE something in order to prove creating
        works can remove it again - see verify_wave4_live.py --create-probe - and for
        the administrator's own dataset maintenance, where removing a stale record IS
        the task: dedupe_material_links.py clears the duplicate way this dataset used
        to say "made from".
        """
        return self._call("DELETE", path, **kw)

    def log(self, action, detail, **extra):
        """Record what this agent did, so the administrator can read the run back."""
        _append(self.activity_log, {
            "at": datetime.now(timezone.utc).isoformat(),
            "agent": self.username, "role": self.role,
            "action": action, "detail": detail, **extra,
        })

    # ── reading ─────────────────────────────────────────────────────────────
    def whoami(self):
        return self.get("/api/auth/me")

    def my_tasks(self, status=None):
        """The workflow tasks assigned to me. This is an agent's inbox."""
        suffix = f"?status={status}" if status else ""
        return self.get(f"/api/tasks{suffix}") or []

    def object(self, part_number):
        """An object header by part number, or None."""
        return self.get(f"/api/plmobjects/{object_id(part_number)}")

    def revisions(self, part_number):
        return self.get(f"/api/plmobjects/{object_id(part_number)}/revisions") or []

    def latest(self, part_number):
        return self.get(f"/api/plmobjects/{object_id(part_number)}/revisions/latest")

    def attributes(self, part_number):
        return self.get(
            f"/api/plmobjects/{object_id(part_number)}/revisions/latest/attributes") or {}

    def bom(self, part_number):
        return self.get(f"/api/plmobjects/{object_id(part_number)}/bom-children") or []

    def where_used(self, part_number):
        return self.get(f"/api/plmobjects/{object_id(part_number)}/bom-parents") or []

    def traces(self, part_number):
        return self.get(
            f"/api/requirement-trace-links/for/{object_id(part_number)}") or {}

    def history(self, part_number):
        latest = self.latest(part_number) or {}
        if not latest.get("revisionId"):
            return []
        return self.get(f"/api/plmobjects/{object_id(part_number)}/revisions/"
                        f"{latest['revisionId']}/history") or []

    def search(self, text):
        return self.get(f"/api/plmobjects/quicksearch?q={requests.utils.quote(text)}")

    def permissions(self, part_number):
        """What this agent may do to this object. The honest answer, from the server."""
        return self.get(f"/api/plmobjects/{object_id(part_number)}/permissions")

    # ── writing ─────────────────────────────────────────────────────────────
    def set_attributes(self, part_number, values, allow_403=False):
        latest = self.latest(part_number)
        if not latest:
            raise Refused("PATCH", part_number, 404, "no latest revision")
        payload = {k: (str(v).lower() if isinstance(v, bool) else v)
                   for k, v in values.items() if v is not None}
        result = self.patch(
            f"/api/plmobjects/{object_id(part_number)}/revisions/"
            f"{latest['revisionId']}/attributes", payload, allow_403=allow_403)
        self.log("set_attributes", f"{part_number}: {', '.join(sorted(payload))}",
                 refused=isinstance(result, Refused))
        return result

    def set_status(self, part_number, status, allow_403=False):
        """Move the latest revision to a new lifecycle state."""
        latest = self.latest(part_number)
        if not latest:
            raise Refused("PUT", part_number, 404, "no latest revision")
        body = dict(latest)
        body["status"] = status
        result = self.put(f"/api/plmobjects/{object_id(part_number)}/revisions/"
                          f"{latest['revisionId']}", body, allow_403=allow_403)
        self.log("set_status", f"{part_number} -> {status}",
                 refused=isinstance(result, Refused))
        return result

    def revise(self, part_number, status=None, allow_403=False):
        """Create the next revision of an object."""
        latest = self.latest(part_number)
        result = self.post(f"/api/plmobjects/{object_id(part_number)}/revisions/"
                           f"{latest['revisionId']}/revise",
                           {"status": status, "minor": False}, allow_403=allow_403)
        self.log("revise", f"{part_number} -> {getattr(result, 'get', lambda _: '?')('revision') if isinstance(result, dict) else 'refused'}",
                 refused=isinstance(result, Refused))
        return result

    def invoke_action(self, part_number, action_name, allow_403=False):
        """Start a type's declared workflow action, e.g. SubmitForRelease."""
        latest = self.latest(part_number)
        result = self.post(f"/api/plmobjects/{object_id(part_number)}/revisions/"
                           f"{latest['revisionId']}/actions/{action_name}/invoke",
                           {}, allow_403=allow_403)
        self.log("invoke_action", f"{part_number}: {action_name}",
                 refused=isinstance(result, Refused))
        return result

    def decide(self, task_id, decision, comment, allow_403=False):
        """Approve or reject a workflow task assigned to me."""
        assert decision in ("Approved", "Rejected")
        result = self.post(f"/api/tasks/{task_id}/decide",
                           {"decision": decision, "comment": comment},
                           allow_403=allow_403)
        self.log("decide", f"task {task_id[:8]}: {decision} - {comment[:120]}",
                 refused=isinstance(result, Refused))
        return result

    def transition_change(self, part_number, route, to_status, comment,
                          allow_403=False):
        """Move an ECR, ECO or ECN. `route` is 'ecrs', 'ecos' or 'ecns'."""
        result = self.post(f"/api/{route}/{object_id(part_number)}/transition",
                           {"toStatus": to_status, "comment": comment},
                           allow_403=allow_403)
        self.log("transition_change", f"{part_number} -> {to_status}: {comment[:120]}",
                 refused=isinstance(result, Refused))
        return result

    # ── talking ─────────────────────────────────────────────────────────────
    def threads(self):
        return self.get("/api/discussions") or []

    def start_thread(self, subject, first_message, participants=None,
                     linked_part_numbers=None, formal=False):
        """Open a discussion thread and post the opening message."""
        existing = next((t for t in self.threads() if t.get("subject") == subject), None)
        if existing:
            thread_id = existing["id"]
        else:
            created = self.post("/api/discussions", {
                "subject": subject,
                "isPrivate": False,
                "participantNames": participants or [],
                "linkedObjectIds": [object_id(p) for p in (linked_part_numbers or [])],
            })
            thread_id = created["id"] if isinstance(created, dict) else created
        self.say_in(thread_id, first_message, formal=formal)
        self.log("start_thread", f"{subject}")
        return thread_id

    def say(self, subject, text, participants=None, linked_part_numbers=None,
            formal=False):
        """Post to a thread by subject, opening it if nobody has yet."""
        thread = next((t for t in self.threads() if t.get("subject") == subject), None)
        if thread is None:
            return self.start_thread(subject, text, participants, linked_part_numbers,
                                     formal=formal)
        self.say_in(thread["id"], text, formal=formal)
        return thread["id"]

    def say_in(self, thread_id, text, formal=False):
        """Post one message. Refuses an essay.

        The first run of this scenario produced 56 messages averaging five thousand
        characters, one of them over twenty thousand - each agent posting a finished
        report with its own headings into a thread nobody was reading yet. That is not
        how a design review sounds. People say one thing, name who they need it from,
        and stop; the next person answers THAT. The length limit is enforced here rather
        than asked for in the brief, because the brief already asked.

        `formal=True` raises the limit for the one case that earns it - a signed
        position, a disposition, a DER decision - which is a document somebody will be
        held to, not a chat message. It is still capped.
        """
        limit = FORMAL_MESSAGE_LIMIT if formal else MESSAGE_LIMIT
        body = (text or "").strip()
        if len(body) > limit:
            raise ValueError(
                f"This message is {len(body)} characters; the limit is {limit}. "
                "Say one thing, name who you need the next thing from, and post it. "
                "Put the detail on the OBJECT - attributes, notes, a finding - where it "
                "can be navigated to, and reference it. If this really is a formal "
                "position somebody will be held to, pass formal=True.")
        self.post(f"/api/discussions/{thread_id}/messages", {"text": body})
        self.log("say", body[:200], thread=thread_id)

    def ask(self, person, subject, text):
        """Open (or continue) a ONE-TO-ONE thread with one colleague and ask them something.

        Most of what these roles need from each other is a question for one person, not an
        announcement to nine. A private thread between two people is how that conversation
        actually happens, and it keeps the shared threads readable - the first run put
        every exchange into two threads, so the record of a change ran to 340,000
        characters and nobody could find the decision in it.
        """
        return self.say(f"{subject} - {self.username} and {person}", text,
                        participants=[person])

    def read_thread(self, subject):
        thread = next((t for t in self.threads() if t.get("subject") == subject), None)
        if thread is None:
            return []
        return self.get(f"/api/discussions/{thread['id']}/messages") or []

    # ── reporting a bug ─────────────────────────────────────────────────────
    def bug(self, app, summary, detail, category="usability", severity="Minor",
            steps=None, expected=None, actual=None, issue_type="Bug"):
        """Report a defect to the PLM administrator.

        An agent never files its own card. The administrator collects these, judges
        them, and files the ones that are real on the Nexus Issues board after the
        project finishes — which is also the only way duplicates get merged rather than
        six agents filing the same thing six times.
        """
        row = {
            "at": datetime.now(timezone.utc).isoformat(),
            "reporter": self.username, "role": self.role,
            "foundInApp": app, "summary": summary, "detail": detail,
            "severity": severity, "issueType": issue_type,
            # security | usability | missing - the three the administrator sorts on.
            "category": category,
            "stepsToReproduce": steps, "expectedResult": expected,
            "actualResult": actual,
            "dateFound": date.today().isoformat(),
        }
        _append(self.bug_log, row)
        self.log("bug", f"[{category}/{severity}] {app}: {summary}")
        return row


def tidy(value, width=110):
    """A long server string, shortened for printing."""
    text = str(value if value is not None else "")
    return text if len(text) <= width else text[:width - 1] + "…"
