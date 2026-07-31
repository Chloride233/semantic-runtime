# Security Policy

## Supported Versions

Semantic Runtime is in pre-alpha (v0.1). No releases are published yet, and
no version is officially supported. Security fixes are applied to `main` and
land in the first stable release.

## Reporting a Vulnerability

Security issues are handled privately. Do not open a public issue.

To report a vulnerability:

- Open a **private security advisory** on GitHub:
  https://github.com/Chloride233/semantic-runtime/security/advisories/new
- Or contact the maintainer via the
  [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) reporting channel.

Please include:

- Affected component (core, models, loaders, context, safety, evidence, mcp)
- Description of the vulnerability and its impact
- Steps to reproduce, if available
- Suggested fix, if you have one

## Response

You should receive an acknowledgement within 7 days. We will coordinate on a
disclosure timeline; by default we follow a 90-day responsible disclosure
window from confirmation to public announcement.

## Scope

This project is infrastructure for AI agents: context resolution, evidence,
and execution between models and tools. Prompt-injection, tool-abuse, and
data-leakage vectors are of particular interest.
