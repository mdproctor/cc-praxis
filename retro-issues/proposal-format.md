# Retrospective Issue Proposal Format

Template for `docs/retro-issues.md` written by Step 7.
Use `#TBD` as the issue number placeholder — replaced with real numbers after creation in Step 8.

```
# Retrospective Issue Mapping
Generated: {date}
Repo: {owner/repo}
Scope: {earliest-date} → {latest-date} | {N} commits analysed
Summary: {N} epics · {N} child issues · {N} standalones · {N} excluded

---

## Epics and Child Issues

### Epic: "{title}" [enhancement]
Period: {start-date} → {end-date}
References: {ADR-NNNN / blog entry date / none}
Scopes: {scope1}, {scope2}

#### Issue #TBD: "{child title}" [enhancement]
Scopes: {scope1}, {scope2}
Commits:
- `{short-hash}` {date} — {message}
- `{short-hash}` {date} — {message}
- `{short-hash}` {date} — {message}

#### Sub-epic: "{sub-epic title}" [enhancement]
Scopes: {scope3}, {scope4}

##### Issue #TBD: "{grandchild title}" [enhancement]
Scopes: {scope3}
Commits:
- `{short-hash}` {date} — {message}
- `{short-hash}` {date} — {message}

##### Issue #TBD: "{grandchild title}" [enhancement]
Scopes: {scope4}
Commits:
- `{short-hash}` {date} — {message}

---

## Standalone Issues

### Issue #TBD: "{title}" [enhancement]
Scopes: {scope1}, {scope2}
Commits:
- `{short-hash}` {date} — {message}
- `{short-hash}` {date} — {message}
- `{short-hash}` {date} — {message}

---

## Excluded Commits (no ticket — trivial only)

This table should be short. If it's long, reconsider the classification.

| Hash | Date | Message | Reason |
|------|------|---------|--------|
| `{hash}` | {date} | {message} | Pure typo fix |
| `{hash}` | {date} | {message} | Whitespace/formatting only |
| `{hash}` | {date} | {message} | Merge commit |
```
