# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ |
| < 1.0   | ❌ |

## Reporting a Vulnerability

THEOS has zero external dependencies in its core (`code/theos_core.py`,
`code/theos_governor.py`, `code/theos_system.py`). The attack surface is small,
but security issues should still be reported responsibly.

**Do not open a public GitHub issue for security vulnerabilities.**

To report a vulnerability:
1. Open a [GitHub Security Advisory](https://github.com/Frederick-Stalnecker/THEOS/security/advisories/new)
   (private, only visible to maintainers)
2. Describe the issue, affected versions, and steps to reproduce
3. You will receive a response within 7 days

## Scope

In scope:
- Code execution vulnerabilities in `code/`
- Dependency vulnerabilities (optional extras: `mcp`, `anthropic`, `openai`, `chromadb`)
- Logic flaws that could cause the governor to make systematically incorrect halt decisions

Out of scope:
- Issues requiring physical access to the machine
- Vulnerabilities in user-supplied LLM API keys or external LLM providers
- Social engineering

## Disclosure

We follow responsible disclosure. Once a fix is ready, we will:
1. Release a patch version
2. Credit the reporter in CHANGELOG.md (unless anonymity is requested)
3. Publish a GitHub Security Advisory

---

*Frederick Davis Stalnecker — maintainer*
