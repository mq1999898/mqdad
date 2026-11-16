# ARD INTELLIGENCE — Initial Repository Audit

Date: 2026-11-16
Repository: mq1999898/mqdad
Audit branch: audit/initial-comprehensive-review
Base commit: 5dca5081e253065c9074dc50417381dffe5b9528

## Scope and evidence

Reviewed README, packaging metadata, environment configuration, model providers, orchestration, agent prompts, SQLite memory, tool registry, approval manager, code staging, research provider, Qt UI, and PowerShell install/launch scripts.

This is a source review. No Windows desktop session, local Ollama service, SSH host, or production environment was available to this audit. A passing CI run is required before describing the project as tested.

## Findings

### High — UI treats chat content as rich HTML
The previous UI used QTextEdit.append with interpolated user and model text. This can interpret text as HTML and create misleading/injected display content. The audit branch changes chat rendering to plain text.

### Medium — unexpected worker exceptions could leave the send control disabled
The Qt worker did not catch exceptions escaping Orchestrator.handle. The audit branch logs unexpected exceptions and emits a generic user-facing error so the UI can recover.

### Medium — no test suite was present at the expected tests paths
The package metadata and README advertised pytest tests, but the expected test files could not be retrieved. This branch adds a deterministic core test suite and a CI workflow for Windows and Ubuntu across Python 3.10–3.13.

### Medium — approval tokens are consumed on a scope mismatch
ApprovalManager removes a token before validating its scope. This is fail-closed and prevents token reuse, but a wrong-scope attempt burns the token. Confirm this is the intended UX before changing it.

### Medium — sandbox is staging plus syntax parsing, not isolation
CodeSandbox writes staged files and parses Python; it does not execute generated code or provide OS-level containment. Do not describe it as a secure execution sandbox.

### Medium — tool registry has no built-in default-deny policy catalogue
Scopes are checked, but the safety of a registered handler depends on the code registering it. Review every registration and handler before enabling system-changing capabilities.

### Medium — provider and research HTTP calls need integration coverage
Ollama, OpenAI-compatible HTTP, and Wikipedia requests have timeouts, but currently lack comprehensive mocked HTTP tests, retry policy, response-size limits, and service-health diagnostics.

### Medium — knowledge FTS fallback and synchronization need more coverage
The store falls back to LIKE when FTS5 is unavailable. Update synchronization and malformed FTS query behavior need explicit tests.

### Low — install script should fail fast on every subprocess failure
PowerShell's Stop preference does not reliably convert every native executable non-zero exit into a terminating error on all supported PowerShell versions. Add explicit exit-code checks and verify under PowerShell 7 on Windows.

## Changes made on this branch

- Render chat messages as plain text rather than HTML.
- Catch unexpected chat worker exceptions and log them.
- Add deterministic tests for settings, memory, approvals, tool scopes, sandbox path handling, and orchestration.
- Add GitHub Actions CI for Windows and Ubuntu on Python 3.10–3.13.
- Keep main unchanged; changes are isolated to this audit branch.

## Not yet verified

- CI execution and test results.
- Actual Windows installation and PySide6 GUI launch.
- Ollama request/response against the user's local llama3.2 service.
- SSH host-key and allow-listed diagnostic command behavior.
- Packaging/build artifact and clean-machine installation.
- End-to-end user workflows.

## Release gate

Do not merge to main or call this production-ready until CI passes, Windows/Ollama smoke tests pass on the target machine, and security-sensitive tool registrations have been reviewed.
