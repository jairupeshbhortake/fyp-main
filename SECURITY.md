# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | ✅ Yes     |
| < 1.0   | ❌ No      |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report security issues privately by emailing **security@example.com** (replace
with your real address). Include:

- A description of the vulnerability
- Steps to reproduce or a proof-of-concept
- The potential impact
- Any suggested mitigations

You will receive an acknowledgement within 48 hours and a resolution timeline
within 7 days.

## Scope

In scope:
- Authentication bypass
- SQL injection or data exposure via the API
- JWT secret leakage

Out of scope:
- Denial-of-service via log file upload (file size limits are a known trade-off)
- Issues in third-party dependencies already tracked upstream

## Disclosure Policy

We follow responsible disclosure. Once a fix is released, we will publish a
security advisory crediting the reporter (unless anonymity is requested).
