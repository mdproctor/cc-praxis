---
name: security-audit
description: >
  Use when user explicitly requests "security review", "audit security", "check
  for vulnerabilities", or "OWASP check", or when code-review identifies
  auth/payment/PII code needing a security pass. NOT automatic — must be
  explicitly requested or offered by code-review. Applies to Java/Quarkus,
  TypeScript, and Python projects.
---

# Security Audit

Reads project type, then loads the language-specific audit checklist.

## Step 0 — Load universal principles

**Load `~/.hortora/garden/approaches/security-audit.md`** before proceeding.

## Step 1 — Detect project type

```bash
python3 ~/.claude/skills/project-init/ctx.py
```

Read `PROJECT_TYPE` from the output.

Extract: `java` | `ts` | `python`

## Step 2 — Load language-specific checklist

| Project type | File to read |
|---|---|
| `java` | `~/.claude/skills/security-audit/java.md` |
| `ts` | `~/.claude/skills/security-audit/typescript.md` |
| `python` | `~/.claude/skills/security-audit/python.md` |

Read the file, then execute the audit workflow it describes.

## Skill Chaining

**Invoked by:** [`code-review`] when auth/payment/PII code is identified; user explicit request

**Does NOT invoke:** other skills automatically — findings are reported only
