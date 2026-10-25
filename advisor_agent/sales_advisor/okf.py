"""Minimal Open Knowledge Format (OKF v0.2) reader for the agent.

A bundle is a directory of markdown files with YAML frontmatter. The concept ID is the file path inside the
bundle without `.md`. `index.md` (per directory) and `log.md` are reserved. Links between concepts are plain
markdown links, absolute (`/policies/x.md`, relative to the bundle root) or relative (`./x.md`).

The agent uses it the way the spec describes: read a directory's index first (progressive disclosure), open a
concept, follow its links. Policy thresholds are custom frontmatter keys, so the same files are readable by
people and machine-operable by code.
"""

from __future__ import annotations

import os
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

RESERVED = {"index.md", "log.md"}
_FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)
_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_INDEX_ENTRY = re.compile(r"^\*\s+\[[^\]]+\]\([^)]+\)(\s+-\s+.+)?$")
_LOG_DATE = re.compile(r"^##\s+\d{4}-\d{2}-\d{2}\s*$")


def default_bundle_path() -> Path:
    env = os.getenv("OKF_BUNDLE")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    return here.parents[2] / "knowledge" / "ezstore-okf"


@dataclass
class Concept:
    id: str
    path: Path
    meta: dict[str, Any]
    body: str
    links: list[str] = field(default_factory=list)

    @property
    def type(self) -> str:
        return str(self.meta.get("type", ""))

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.id.rsplit("/", 1)[-1])

    @property
    def description(self) -> str:
        return str(self.meta.get("description", ""))

    def summary(self) -> dict[str, Any]:
        return {"id": self.id, "type": self.type, "title": self.title, "description": self.description}


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    m = _FRONTMATTER.match(text)
    if not m:
        return None, text
    meta = yaml.safe_load(m.group(1))
    return (meta if isinstance(meta, dict) else None), m.group(2)


def resolve_link(from_id: str, target: str) -> str | None:
    """Markdown link target → concept ID (None for external URLs / directories)."""
    if re.match(r"^[a-z]+://", target) or target.startswith("#") or target.startswith("mailto:"):
        return None
    target = target.split("#", 1)[0]
    if not target.endswith(".md"):
        return None
    if target.startswith("/"):
        path = target.lstrip("/")
    else:
        base = posixpath.dirname(from_id)
        path = posixpath.normpath(posixpath.join(base, target))
    return path[:-3]


class Bundle:
    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else default_bundle_path()
        if not self.root.is_dir():
            raise FileNotFoundError(f"OKF bundle not found: {self.root}")
        self.concepts: dict[str, Concept] = {}
        for path in sorted(self.root.rglob("*.md")):
            if path.name in RESERVED:
                continue
            rel = path.relative_to(self.root).as_posix()
            cid = rel[:-3]
            meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
            meta = meta or {}
            links = [lid for _, t in _LINK.findall(body) if (lid := resolve_link(cid, t))]
            self.concepts[cid] = Concept(cid, path, meta, body.strip(), sorted(set(links)))

    # ---- progressive disclosure -------------------------------------------------
    def index(self, directory: str = "") -> str:
        directory = directory.strip("/")
        path = self.root / directory / "index.md"
        if path.is_file():
            _, body = split_frontmatter(path.read_text(encoding="utf-8"))
            return body.strip()
        # synthesize when missing (allowed by the spec)
        prefix = f"{directory}/" if directory else ""
        lines = [f"# {directory or 'bundle'}"]
        for c in self.concepts.values():
            if c.id.startswith(prefix) and "/" not in c.id[len(prefix):]:
                lines.append(f"* [{c.title}](/{c.id}.md) - {c.description}")
        return "\n".join(lines)

    def get(self, concept_id: str) -> Concept | None:
        cid = concept_id.strip().lstrip("/")
        cid = cid[:-3] if cid.endswith(".md") else cid
        return self.concepts.get(cid)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Keyword search over title / description / tags / body (title and description weigh more)."""
        q = query.strip().lower()
        if not q:
            return []
        terms = [t for t in re.split(r"[\s,，、。?？]+", q) if t]
        # CJK queries often have no spaces: also use 2-character shingles
        grams: list[str] = []
        for t in terms:
            if re.search(r"[一-鿿]", t) and len(t) > 2:
                grams += [t[i : i + 2] for i in range(len(t) - 1)]
        scored = []
        for c in self.concepts.values():
            head = f"{c.id} {c.title} {c.description} {' '.join(map(str, c.meta.get('tags') or []))}".lower()
            body = c.body.lower()
            score = 0.0
            for t in terms:
                score += 5 * head.count(t) + body.count(t)
            for g in grams:
                score += 1.0 * head.count(g) + 0.2 * body.count(g)
            if score > 0:
                scored.append((score, c))
        scored.sort(key=lambda x: (-x[0], x[1].id))
        return [{**c.summary(), "score": round(s, 1)} for s, c in scored[:top_k]]

    def backlinks(self, concept_id: str) -> list[str]:
        return sorted(c.id for c in self.concepts.values() if concept_id in c.links)

    # ---- conformance ------------------------------------------------------------
    def validate(self) -> list[str]:
        """Problems that make the bundle non-conformant with OKF v0.2 (empty list = conformant)."""
        problems: list[str] = []
        for path in sorted(self.root.rglob("*.md")):
            rel = path.relative_to(self.root).as_posix()
            text = path.read_text(encoding="utf-8")
            if path.name == "index.md":
                meta, body = split_frontmatter(text)
                if meta is not None and (rel != "index.md" or set(meta) - {"okf_version"}):
                    problems.append(f"{rel}: only the bundle-root index.md may have frontmatter (okf_version)")
                for line in body.splitlines():
                    if line.startswith("* ") and not _INDEX_ENTRY.match(line.strip()):
                        problems.append(f"{rel}: index entry should be '* [Title](url) - description': {line}")
                if not re.search(r"^#\s", body, re.M):
                    problems.append(f"{rel}: index.md needs at least one '#' section heading")
            elif path.name == "log.md":
                dates = [ln for ln in text.splitlines() if ln.startswith("## ")]
                bad = [d for d in dates if not _LOG_DATE.match(d)]
                if bad:
                    problems.append(f"{rel}: log date headings must be '## YYYY-MM-DD': {bad}")
                iso = [d[3:].strip() for d in dates if _LOG_DATE.match(d)]
                if iso != sorted(iso, reverse=True):
                    problems.append(f"{rel}: log entries must be newest first")
            else:
                meta, _ = split_frontmatter(text)
                if meta is None:
                    problems.append(f"{rel}: missing or unparseable YAML frontmatter")
                elif not str(meta.get("type", "")).strip():
                    problems.append(f"{rel}: frontmatter needs a non-empty 'type'")
        return problems

    def broken_links(self) -> list[tuple[str, str]]:
        """Allowed by the spec (not-yet-written knowledge) but worth reporting."""
        return [(c.id, link) for c in self.concepts.values() for link in c.links if link not in self.concepts]

    # ---- machine-operable policy values -----------------------------------------
    def policy(self) -> dict[str, Any]:
        tiers = (self.get("policies/pricing-factor-by-tier") or Concept("", Path(), {}, "")).meta.get("policy_tiers", {})
        margin = (self.get("policies/minimum-profit-rate") or Concept("", Path(), {}, "")).meta
        credit = (self.get("policies/customer-credit-policy") or Concept("", Path(), {}, "")).meta.get("credit_rules", [])
        return {
            "tiers": tiers,
            "min_profit_rate": float(margin.get("min_profit_rate", 0.25)),
            "approval_profit_rate": float(margin.get("approval_profit_rate", 0.30)),
            "credit_rules": sorted(credit, key=lambda r: r["below"]),
        }
