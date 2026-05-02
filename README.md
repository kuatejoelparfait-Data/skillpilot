# skillpilot

**228 AI skills for Claude Code — install, run and manage skills directly in your terminal.**

[![PyPI version](https://img.shields.io/pypi/v/skillpilot.svg)](https://pypi.org/project/skillpilot/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is skillpilot?

**skillpilot** is a CLI that gives you instant access to **228 expert AI skills** designed for [Claude Code](https://claude.ai/code). Browse, install, copy and run skills covering engineering, security, marketing, finance, product, compliance and more — all from your terminal.

Each skill is a battle-tested prompt that turns Claude into a domain expert:

- `code-reviewer` → Senior code review with security + quality analysis
- `tdd` → Test-driven development workflow
- `seo-audit` → Full SEO audit of your content
- `financial-analyst` → Financial analysis and SaaS metrics
- `incident-response` → SEV1–SEV4 incident triage and response
- ...and 223 more

---

## Installation

```bash
pip install skillpilot
```

Requires Python 3.10+ and [Claude Code](https://claude.ai/code) installed.

---

## Quick Start

```bash
# 1. Browse the catalogue
skillpilot list

# 2. Search for a skill
skillpilot search security

# 3. Preview a skill
skillpilot info code-reviewer

# 4. Install a skill into Claude Code
skillpilot install code-reviewer
# → Use /code-reviewer in Claude Code

# 5. Install all skills at once
skillpilot install-all

# 6. Copy a skill to clipboard
skillpilot copy tdd

# 7. Run a skill via API (requires init)
skillpilot init
skillpilot run code-reviewer --input "$(cat myfile.py)"
```

---

## Commands

| Command | Description |
|---|---|
| `skillpilot list` | List all 228 skills by category |
| `skillpilot list -c engineering` | List skills in a specific category |
| `skillpilot search <keyword>` | Search skills by keyword |
| `skillpilot info <skill>` | Preview first 20 lines of a skill |
| `skillpilot install <skill>` | Install a skill into `~/.claude/commands/` |
| `skillpilot install-all` | Install all 228 skills into Claude Code |
| `skillpilot install-all -c marketing` | Install an entire category |
| `skillpilot copy <skill>` | Copy skill content to clipboard |
| `skillpilot run <skill> --input "..."` | Execute a skill via Anthropic API |
| `skillpilot init` | Save your Anthropic API key |

---

## Skill Categories

| Category | Skills | Description |
|---|---|---|
| `engineering` | 48 | POWERFUL-tier: agents, RAG, MCP, CI/CD, databases |
| `engineering-team` | 35 | Core: code review, TDD, security, cloud architecture |
| `commands` | 29 | Slash commands: /tdd, /tech-debt, /sprint-plan... |
| `marketing` | 44 | SEO, content, ads, CRO, social media |
| `product` | 16 | Product management, UX, roadmap, experiments |
| `strategy` | 28 | C-Level advisory: CEO, CTO, CFO, CMO... |
| `project-management` | 8 | Jira, Confluence, Scrum, sprint planning |
| `compliance` | 13 | GDPR, ISO 13485, MDR, SOC2, ISO 27001 |
| `business` | 4 | Sales engineering, customer success, RevOps |
| `finance` | 3 | Financial analysis, SaaS metrics, investment |

---

## Installing Skills into Claude Code

When you run `skillpilot install <skill>`, the skill is copied to `~/.claude/commands/<skill>.md`. Claude Code automatically picks it up as a slash command:

```bash
skillpilot install tdd
# Now use /tdd in Claude Code
```

Install an entire category:
```bash
skillpilot install-all --category engineering
# All 48 engineering skills available as /skill-name in Claude Code
```

Install everything:
```bash
skillpilot install-all
# All 228 skills available in Claude Code
```

---

## Running Skills via API

For running skills directly from the terminal without Claude Code:

```bash
# Configure your Anthropic API key (once)
skillpilot init

# Run any skill
skillpilot run code-reviewer --input "def add(a, b): return a + b"

# Pipe code from a file
skillpilot run security-pen-testing --input "$(cat app.py)"

# Interactive mode (paste code, then Ctrl+D)
skillpilot run tdd
```

Skills use **Claude Haiku** by default — fast and cost-effective.

---

## Project Structure

```
skillpilot/
├── src/devpilot/
│   ├── cli.py              # CLI commands (Typer)
│   ├── core/
│   │   ├── claude.py       # Anthropic API client
│   │   ├── config.py       # Local config (~/.devpilot/)
│   │   └── skills.py       # Skill loader
│   └── skills/             # 228 embedded skill files
│       ├── engineering/    # 48 skills
│       ├── engineering-team/ # 35 skills
│       ├── marketing/      # 44 skills
│       ├── product/        # 16 skills
│       ├── strategy/       # 28 skills
│       ├── project-management/ # 8 skills
│       ├── compliance/     # 13 skills
│       ├── business/       # 4 skills
│       ├── finance/        # 3 skills
│       └── commands/       # 29 slash commands
├── scripts/
│   ├── sync_skills.py      # Sync skills from source library
│   └── generate_license.py # License key generator
└── tests/                  # 23 tests (pytest)
```

---

## Development

```bash
git clone https://github.com/DigitalHouseCompany/skillpilot
cd skillpilot
pip install -e .
pytest tests/ -v
```

To sync skills from the source library:
```bash
python scripts/sync_skills.py
```

---

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/code) (for `install` commands)
- Anthropic API key (for `run` command only)

---

## License

MIT — see [LICENSE](LICENSE)

---

## Author

Built by [Joel Parfait](mailto:joelparfait237@gmail.com)  
PyPI: [pypi.org/project/skillpilot](https://pypi.org/project/skillpilot/)
