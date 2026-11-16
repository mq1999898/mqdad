# ARD INTELLIGENCE

ARD INTELLIGENCE is a Windows-first, extensible multi-agent desktop AI foundation. It combines an Ollama-compatible local model, an optional OpenAI-compatible provider, SQLite memory, modular research and agent interfaces, and explicit approval gates for sensitive operations.

> **Foundation status:** This repository contains a working starter application, core modules, and automated tests. It is not a hardened operating system sandbox, autonomous offensive security tool, or production-ready agent. Review every proposed action. No model-generated shell command is executed by this project.

## Features

- Task orchestration across Research, Knowledge, Developer, Cybersecurity, Windows, and Kali specialist agents.
- Local Ollama HTTP provider and optional OpenAI-compatible remote provider (enabled only by configuration).
- SQLite conversation memory and FTS5 searchable knowledge store.
- Tool registry with authorization scopes and one-time human approval tokens.
- Defensive-only, fixed-command Kali SSH adapter; Paramiko is optional and SSH host keys are verified.
- Wikipedia research provider interface with timeouts and a configurable web research abstraction.
- Code staging workflow that rejects path traversal, parses Python without executing it, and requires approval before deployment.
- Optional PySide6 chat window and system status dashboard.
- Audit logging, PowerShell setup/launch scripts, and pytest suite.

## Installation (Windows 11 Pro)

1. Install Python 3.10 or later and (optionally) [Ollama](https://ollama.com/download/windows).
2. Clone this repository and open PowerShell in its directory.
3. Run `./scripts/install.ps1`. It creates `.venv`, installs the package, and installs the desktop and test extras.
4. Optionally start Ollama and pull a model, for example `ollama pull llama3.2`.
5. Copy `.env.example` to `.env` and adjust settings. Never commit `.env` or put secrets in source control.
6. Launch with `./scripts/start.ps1` or `.venv/Scripts/ard-intelligence.exe`.

For a headless/core install, use `python -m pip install -e ".[test]"`. Run tests with `python -m pytest`.

## Configuration

Environment variables (also documented in `.env.example`):

- `ARD_MODEL_PROVIDER`: `ollama` (default), `openai_compatible`, or `offline`.
- `ARD_OLLAMA_URL`, `ARD_OLLAMA_MODEL`: local Ollama endpoint and model.
- `ARD_REMOTE_BASE_URL`, `ARD_REMOTE_MODEL`, `ARD_REMOTE_API_KEY`: optional compatible API. The key is read from the environment only.
- `ARD_DATA_DIR`: database/log/staging directory (defaults to `~/.ard-intelligence`).

Remote access is opt-in. The application does not send data to a remote provider unless the provider is explicitly selected. Treat model output as untrusted.

## Safety and authorization

- The tool registry checks declared scopes and requires a one-use approval token for sensitive actions.
- Kali SSH supports only a short built-in list of read-only diagnostic commands; it does not accept model-supplied command strings. Configure a trusted `known_hosts` file and use key-based authentication.
- The developer workflow stages source and performs syntax validation only; it does not run generated code. Deployment is deliberately not implemented. A human approval gate is required to mark a staged artifact approved, but this is not a secure sandbox or an automatic deployment mechanism.
- Cybersecurity agent behavior is limited to authorized defensive planning and general analysis. It performs no scanning, exploitation, persistence, or target interaction.
- Do not use this foundation against systems without explicit authorization. Add additional policy, isolation, and review before connecting tools that can change systems or access sensitive data.

## Project layout

- `src/ard_intelligence/`: application, orchestration, providers, agents, memory, approval, tools, SSH, sandbox, logging.
- `tests/`: deterministic tests for core logic; no network, SSH, or model credentials are needed.
- `scripts/`: Windows PowerShell installer and launcher.

## Current limitations

The desktop UI is intentionally minimal. Ollama/remote APIs, live Wikipedia lookup, and SSH need their corresponding services/configuration and were not integration-tested here. SSH requires optional Paramiko and trusted host-key configuration. The staged-code workflow does not provide OS-level sandboxing and will not execute generated code. There is no deployment adapter, plugin package loader, Windows/Kali system-control tool, or autonomous cybersecurity action. These are intentionally left unimplemented until a secure threat model and explicit approval UX are designed.
