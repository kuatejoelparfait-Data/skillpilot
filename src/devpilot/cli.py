import sys
import shutil
import subprocess
from pathlib import Path
from importlib.metadata import version as pkg_version

import typer
import keyring
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import print as rprint

from devpilot.core.skills import SkillLoader
from devpilot.core.claude import ClaudeClient

# ── app ───────────────────────────────────────────────────────────────────────

app = typer.Typer(
    help=(
        "[bold cyan]skillpilot[/bold cyan] — 228 AI skills for [bold]Claude Code[/bold]\n\n"
        "Install, run, manage and explore AI skills directly in your Claude Code workflow.\n\n"
        "[dim]Docs: https://github.com/kuatejoelparfait-Data/skillpilot[/dim]"
    ),
    no_args_is_help=True,
    rich_markup_mode="rich",
    epilog=(
        "[bold]Quick start:[/bold]\n"
        "  skillpilot list                        # browse all 228 skills\n"
        "  skillpilot search security             # find skills by keyword\n"
        "  skillpilot install code-reviewer       # install into Claude Code\n"
        "  skillpilot run tdd --input 'my code'   # run via Anthropic API\n\n"
        "[bold]Workflow:[/bold] search → info → install → use /skill in Claude Code"
    ),
)
console = Console()
KEYRING_SERVICE = "skillpilot"
CLAUDE_COMMANDS_DIR = Path.home() / ".claude" / "commands"


# ── internal helpers ──────────────────────────────────────────────────────────

def _get_api_key() -> str | None:
    return keyring.get_password(KEYRING_SERVICE, "api_key")


def _ensure_claude_dir() -> bool:
    try:
        CLAUDE_COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def _installed_skills() -> list[str]:
    if not CLAUDE_COMMANDS_DIR.exists():
        return []
    return sorted([f.stem for f in CLAUDE_COMMANDS_DIR.glob("*.md")])


# ══════════════════════════════════════════════════════════════════════════════
# SETUP
# ══════════════════════════════════════════════════════════════════════════════

@app.command()
def init():
    """[SETUP] Configure your Anthropic API key for [cyan]skillpilot run[/cyan]."""
    api_key = typer.prompt("Anthropic API key (sk-ant-...)", hide_input=True)
    keyring.set_password(KEYRING_SERVICE, "api_key", api_key)
    rprint("[green]✓ API key saved securely.[/green]")
    rprint("[dim]Run: skillpilot doctor  — to verify your setup[/dim]")


@app.command()
def doctor():
    """[SETUP] Check your skillpilot setup (Claude Code, API key, install dir)."""
    checks = []

    # Claude Code install dir
    if CLAUDE_COMMANDS_DIR.exists():
        checks.append(("[green]✓[/green]", "Claude Code commands dir", str(CLAUDE_COMMANDS_DIR)))
    else:
        checks.append(("[yellow]~[/yellow]", "Claude Code commands dir", f"{CLAUDE_COMMANDS_DIR} (will be created on install)"))

    # API key
    key = _get_api_key()
    if key:
        checks.append(("[green]✓[/green]", "Anthropic API key", f"sk-ant-...{key[-6:]}"))
    else:
        checks.append(("[red]✗[/red]", "Anthropic API key", "Not set — run: skillpilot init"))

    # Skills available
    loader = SkillLoader()
    total = sum(len(loader.list_category(c)) for c in loader.categories())
    checks.append(("[green]✓[/green]", "Skills available", f"{total} skills across {len(loader.categories())} categories"))

    # Installed
    installed = _installed_skills()
    checks.append(("[green]✓[/green]" if installed else "[dim]-[/dim]", "Skills installed", f"{len(installed)} installed in Claude Code"))

    table = Table(title="skillpilot — Doctor", show_header=False, box=None)
    table.add_column("", style="bold", width=3)
    table.add_column("Check", style="cyan", min_width=25)
    table.add_column("Details")
    for status, name, detail in checks:
        table.add_row(status, name, detail)
    console.print(table)


@app.command()
def version():
    """[SETUP] Show skillpilot version."""
    try:
        v = pkg_version("skillpilot")
    except Exception:
        v = "0.3.0"
    rprint(f"[bold cyan]skillpilot[/bold cyan] v{v}")
    rprint("[dim]PyPI: https://pypi.org/project/skillpilot/[/dim]")


# ══════════════════════════════════════════════════════════════════════════════
# DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════

@app.command(name="list")
def list_skills(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category name"),
):
    """[DISCOVER] List all 228 skills by category."""
    loader = SkillLoader()

    if category:
        skills = loader.list_category(category)
        if not skills:
            rprint(f"[red]✗ Category '{category}' not found.[/red]")
            rprint(f"[dim]Run: skillpilot categories  — to see available categories[/dim]")
            raise typer.Exit(1)
        installed = set(_installed_skills())
        table = Table(title=f"[bold]{category}[/bold] — {len(skills)} skills")
        table.add_column("Skill", style="cyan")
        table.add_column("Installed", justify="center")
        for s in skills:
            table.add_row(s, "[green]✓[/green]" if s in installed else "")
        console.print(table)
        return

    all_data = loader.list_all()
    total = sum(len(v["skills"]) for v in all_data.values())
    installed = set(_installed_skills())
    table = Table(title=f"[bold cyan]skillpilot[/bold cyan] — {total} AI skills for Claude Code")
    table.add_column("Category", style="cyan")
    table.add_column("Skills", justify="right", style="green")
    table.add_column("Installed", justify="right", style="yellow")
    for cat, info in sorted(all_data.items()):
        cat_skills = set(info["skills"])
        n_installed = len(cat_skills & installed)
        table.add_row(cat, str(len(info["skills"])), str(n_installed) if n_installed else "—")
    console.print(table)
    rprint(f"\n[dim]skillpilot list -c <category>   →  list skills in a category[/dim]")
    rprint(f"[dim]skillpilot install <skill>       →  install into Claude Code[/dim]")
    rprint(f"[dim]skillpilot installed             →  see what's installed[/dim]")


@app.command()
def categories():
    """[DISCOVER] List all skill categories."""
    loader = SkillLoader()
    cats = loader.categories()
    panels = []
    for cat in cats:
        skills = loader.list_category(cat)
        panels.append(Panel(f"[green]{len(skills)} skills[/green]", title=f"[cyan]{cat}[/cyan]", expand=True))
    console.print(Columns(panels))
    rprint(f"\n[dim]skillpilot list -c <category>  →  see skills in a category[/dim]")


@app.command()
def search(
    keyword: str = typer.Argument(..., help="Keyword to search across all skill names"),
):
    """[DISCOVER] Search skills by keyword across all categories."""
    loader = SkillLoader()
    results = loader.search(keyword)
    if not results:
        rprint(f"[yellow]No skill found for '{keyword}'[/yellow]")
        raise typer.Exit(1)
    installed = set(_installed_skills())
    table = Table(title=f"{len(results)} result(s) for '[bold]{keyword}[/bold]'")
    table.add_column("Skill", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Installed", justify="center")
    for r in results:
        table.add_row(r["skill"], r["category"], "[green]✓[/green]" if r["skill"] in installed else "")
    console.print(table)
    rprint(f"\n[dim]skillpilot info <skill>     →  preview a skill[/dim]")
    rprint(f"[dim]skillpilot install <skill>  →  install into Claude Code[/dim]")


@app.command()
def stats():
    """[DISCOVER] Show stats about available and installed skills."""
    loader = SkillLoader()
    installed = set(_installed_skills())
    all_data = loader.list_all()
    total = sum(len(v["skills"]) for v in all_data.values())
    total_installed = len(installed)

    table = Table(title="skillpilot — Stats", show_header=False, box=None)
    table.add_column("Metric", style="cyan", min_width=25)
    table.add_column("Value", style="bold green")
    table.add_row("Total skills available", str(total))
    table.add_row("Skills installed", f"{total_installed} ({int(total_installed/total*100)}%)" if total else "0")
    table.add_row("Categories", str(len(all_data)))
    table.add_row("Install directory", str(CLAUDE_COMMANDS_DIR))
    console.print(table)

    if total_installed < total:
        rprint(f"\n[yellow]💡 {total - total_installed} skills not yet installed.[/yellow]")
        rprint("[dim]Run: skillpilot install-all  — to install everything[/dim]")


# ══════════════════════════════════════════════════════════════════════════════
# READING
# ══════════════════════════════════════════════════════════════════════════════

@app.command()
def info(
    skill: str = typer.Argument(..., help="Skill name"),
):
    """[READ] Preview first 20 lines of a skill."""
    loader = SkillLoader()
    result = loader.find(skill)
    if not result:
        rprint(f"[red]✗ Skill '{skill}' not found.[/red]")
        rprint(f"[dim]Run: skillpilot search {skill}[/dim]")
        raise typer.Exit(1)
    cat, path = result
    lines = path.read_text(encoding="utf-8").split("\n")[:20]
    console.rule(f"[bold cyan]{skill}[/bold cyan] [dim]({cat})[/dim]")
    console.print("\n".join(lines))
    console.rule()
    rprint(f"\n[dim]skillpilot show {skill}     →  full content[/dim]")
    rprint(f"[dim]skillpilot install {skill}  →  install into Claude Code[/dim]")
    rprint(f"[dim]skillpilot run {skill}      →  run via API[/dim]")


@app.command()
def show(
    skill: str = typer.Argument(..., help="Skill name"),
    category: str = typer.Option(None, "--category", "-c"),
):
    """[READ] Show the full content of a skill."""
    loader = SkillLoader()
    try:
        content = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)
    result = loader.find(skill)
    cat = result[0] if result else "unknown"
    console.rule(f"[bold cyan]{skill}[/bold cyan] [dim]({cat})[/dim]")
    console.print(content)
    console.rule()


@app.command()
def export(
    skill: str = typer.Argument(..., help="Skill name to export"),
    output: Path = typer.Option(None, "--output", "-o", help="Output file path (default: ./<skill>.md)"),
    category: str = typer.Option(None, "--category", "-c"),
):
    """[READ] Export a skill to a markdown file."""
    loader = SkillLoader()
    try:
        content = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)
    dest = output or Path(f"{skill}.md")
    dest.write_text(content, encoding="utf-8")
    rprint(f"[green]✓ '{skill}' exported to {dest}[/green]")


@app.command(name="export-all")
def export_all(
    output_dir: Path = typer.Option(Path("./skills-export"), "--output", "-o", help="Output directory"),
    category: str = typer.Option(None, "--category", "-c", help="Export a single category"),
):
    """[READ] Export all skills (or a category) to a local directory."""
    loader = SkillLoader()
    output_dir.mkdir(parents=True, exist_ok=True)
    cats = [category] if category else loader.categories()
    total = 0
    for cat in cats:
        cat_dir = output_dir / cat
        cat_dir.mkdir(exist_ok=True)
        for skill_name in loader.list_category(cat):
            try:
                content = loader.load(skill_name, category=cat)
                (cat_dir / f"{skill_name}.md").write_text(content, encoding="utf-8")
                total += 1
            except Exception:
                pass
    rprint(f"[green]✓ {total} skills exported to {output_dir}/[/green]")


# ══════════════════════════════════════════════════════════════════════════════
# INSTALL / UNINSTALL
# ══════════════════════════════════════════════════════════════════════════════

@app.command()
def install(
    skill: str = typer.Argument(..., help="Skill name to install into Claude Code"),
    category: str = typer.Option(None, "--category", "-c", help="Skill category"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if already installed"),
):
    """[INSTALL] Install a skill into Claude Code (~/.claude/commands/)."""
    loader = SkillLoader()
    try:
        content = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    if not _ensure_claude_dir():
        rprint("[red]✗ Cannot create ~/.claude/commands/. Is Claude Code installed?[/red]")
        raise typer.Exit(1)

    dest = CLAUDE_COMMANDS_DIR / f"{skill}.md"
    if dest.exists() and not force:
        rprint(f"[yellow]~ '{skill}' already installed. Use --force to overwrite.[/yellow]")
        return

    dest.write_text(content, encoding="utf-8")
    rprint(f"[green]✓ '{skill}' installed in Claude Code.[/green]")
    rprint(f"[dim]Use /{skill} in Claude Code to activate it.[/dim]")


@app.command(name="install-all")
def install_all(
    category: str = typer.Option(None, "--category", "-c", help="Install a single category"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite already installed skills"),
):
    """[INSTALL] Install all skills (or a category) into Claude Code."""
    loader = SkillLoader()

    if not _ensure_claude_dir():
        rprint("[red]✗ Cannot create ~/.claude/commands/.[/red]")
        raise typer.Exit(1)

    cats = [category] if category else loader.categories()
    total, skipped = 0, 0
    for cat in cats:
        for skill_name in loader.list_category(cat):
            dest = CLAUDE_COMMANDS_DIR / f"{skill_name}.md"
            if dest.exists() and not force:
                skipped += 1
                continue
            try:
                content = loader.load(skill_name, category=cat)
                dest.write_text(content, encoding="utf-8")
                total += 1
            except Exception:
                pass

    rprint(f"[green]✓ {total} skills installed in {CLAUDE_COMMANDS_DIR}[/green]")
    if skipped:
        rprint(f"[dim]{skipped} skipped (already installed). Use --force to overwrite.[/dim]")
    rprint("[dim]Restart Claude Code to see them as /skill-name commands.[/dim]")


@app.command()
def update(
    skill: str = typer.Argument(..., help="Skill name to update"),
    category: str = typer.Option(None, "--category", "-c"),
):
    """[INSTALL] Update an installed skill to the latest version."""
    dest = CLAUDE_COMMANDS_DIR / f"{skill}.md"
    if not dest.exists():
        rprint(f"[yellow]~ '{skill}' is not installed. Run: skillpilot install {skill}[/yellow]")
        raise typer.Exit(1)

    loader = SkillLoader()
    try:
        content = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    dest.write_text(content, encoding="utf-8")
    rprint(f"[green]✓ '{skill}' updated.[/green]")


@app.command(name="update-all")
def update_all():
    """[INSTALL] Update all currently installed skills to their latest version."""
    installed = _installed_skills()
    if not installed:
        rprint("[yellow]No skills installed. Run: skillpilot install-all[/yellow]")
        raise typer.Exit(1)

    loader = SkillLoader()
    updated, failed = 0, 0
    for skill_name in installed:
        result = loader.find(skill_name)
        if not result:
            failed += 1
            continue
        cat, path = result
        dest = CLAUDE_COMMANDS_DIR / f"{skill_name}.md"
        try:
            dest.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
            updated += 1
        except Exception:
            failed += 1

    rprint(f"[green]✓ {updated} skills updated.[/green]")
    if failed:
        rprint(f"[yellow]{failed} failed.[/yellow]")


@app.command()
def uninstall(
    skill: str = typer.Argument(..., help="Skill name to remove from Claude Code"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """[INSTALL] Remove a skill from Claude Code (~/.claude/commands/)."""
    dest = CLAUDE_COMMANDS_DIR / f"{skill}.md"
    if not dest.exists():
        rprint(f"[yellow]~ '{skill}' is not installed.[/yellow]")
        raise typer.Exit(1)

    if not yes:
        typer.confirm(f"Remove '{skill}' from Claude Code?", abort=True)

    dest.unlink()
    rprint(f"[green]✓ '{skill}' removed.[/green]")


@app.command(name="uninstall-all")
def uninstall_all(
    category: str = typer.Option(None, "--category", "-c", help="Remove a single category"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """[INSTALL] Remove all installed skills from Claude Code."""
    installed = _installed_skills()
    if not installed:
        rprint("[yellow]No skills installed.[/yellow]")
        raise typer.Exit(1)

    if category:
        loader = SkillLoader()
        cat_skills = set(loader.list_category(category))
        to_remove = [s for s in installed if s in cat_skills]
    else:
        to_remove = installed

    if not to_remove:
        rprint(f"[yellow]No installed skills found for category '{category}'.[/yellow]")
        raise typer.Exit(1)

    if not yes:
        typer.confirm(f"Remove {len(to_remove)} skill(s) from Claude Code?", abort=True)

    removed = 0
    for skill_name in to_remove:
        dest = CLAUDE_COMMANDS_DIR / f"{skill_name}.md"
        if dest.exists():
            dest.unlink()
            removed += 1

    rprint(f"[green]✓ {removed} skills removed.[/green]")


@app.command()
def installed():
    """[INSTALL] List all skills currently installed in Claude Code."""
    skills = _installed_skills()
    if not skills:
        rprint("[yellow]No skills installed yet.[/yellow]")
        rprint("[dim]Run: skillpilot install-all  — to install everything[/dim]")
        raise typer.Exit(1)

    loader = SkillLoader()
    table = Table(title=f"Installed in Claude Code ({len(skills)} skills)")
    table.add_column("Skill", style="cyan")
    table.add_column("Category", style="magenta")
    for s in skills:
        result = loader.find(s)
        cat = result[0] if result else "unknown"
        table.add_row(s, cat)
    console.print(table)
    rprint(f"\n[dim]Use /skill-name in Claude Code to activate any skill.[/dim]")


# ══════════════════════════════════════════════════════════════════════════════
# CLIPBOARD
# ══════════════════════════════════════════════════════════════════════════════

@app.command()
def copy(
    skill: str = typer.Argument(..., help="Skill name to copy to clipboard"),
    category: str = typer.Option(None, "--category", "-c"),
):
    """[CLIPBOARD] Copy a skill's content to the clipboard."""
    loader = SkillLoader()
    try:
        content = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    try:
        if sys.platform == "win32":
            subprocess.run("clip", input=content.encode("utf-16"), check=True, shell=True)
        elif sys.platform == "darwin":
            subprocess.run("pbcopy", input=content.encode(), check=True)
        else:
            subprocess.run(["xclip", "-selection", "clipboard"], input=content.encode(), check=True)
        rprint(f"[green]✓ '{skill}' copied to clipboard.[/green]")
        rprint("[dim]Paste it directly into Claude Code or Claude.ai.[/dim]")
    except Exception:
        rprint("[yellow]Clipboard unavailable. Showing content instead:[/yellow]\n")
        console.print(content)


# ══════════════════════════════════════════════════════════════════════════════
# EXECUTION
# ══════════════════════════════════════════════════════════════════════════════

@app.command()
def run(
    skill: str = typer.Argument(..., help="Skill name to execute"),
    category: str = typer.Option(None, "--category", "-c", help="Skill category"),
    input_text: str = typer.Option(None, "--input", "-i", help="Text or code to analyze"),
    output: Path = typer.Option(None, "--output", "-o", help="Save result to a file"),
):
    """[RUN] Execute a skill via the Anthropic API (requires skillpilot init)."""
    api_key = _get_api_key()
    if not api_key:
        rprint("[red]✗ No API key. Run: skillpilot init[/red]")
        raise typer.Exit(1)

    loader = SkillLoader()
    try:
        prompt = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    if not input_text:
        rprint("[yellow]Paste your code/text (Ctrl+D to submit):[/yellow]")
        input_text = sys.stdin.read()

    with console.status(f"[bold green]Running '{skill}' via Claude..."):
        result = ClaudeClient(api_key=api_key).run(skill_prompt=prompt, user_input=input_text)

    console.rule(f"[bold]Result — {skill}[/bold]")
    console.print(result)
    console.rule()

    if output:
        output.write_text(result, encoding="utf-8")
        rprint(f"\n[green]✓ Result saved to {output}[/green]")


@app.command(name="run-file")
def run_file(
    skill: str = typer.Argument(..., help="Skill name to execute"),
    file: Path = typer.Argument(..., help="File to analyze (e.g. app.py, README.md)"),
    category: str = typer.Option(None, "--category", "-c"),
    output: Path = typer.Option(None, "--output", "-o", help="Save result to a file"),
):
    """[RUN] Run a skill on a local file (e.g. skillpilot run-file code-reviewer app.py)."""
    if not file.exists():
        rprint(f"[red]✗ File '{file}' not found.[/red]")
        raise typer.Exit(1)

    api_key = _get_api_key()
    if not api_key:
        rprint("[red]✗ No API key. Run: skillpilot init[/red]")
        raise typer.Exit(1)

    loader = SkillLoader()
    try:
        prompt = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    input_text = file.read_text(encoding="utf-8", errors="ignore")
    rprint(f"[dim]Running '{skill}' on {file} ({len(input_text)} chars)...[/dim]")

    with console.status(f"[bold green]Analyzing {file.name} with '{skill}'..."):
        result = ClaudeClient(api_key=api_key).run(skill_prompt=prompt, user_input=input_text)

    console.rule(f"[bold]Result — {skill} on {file.name}[/bold]")
    console.print(result)
    console.rule()

    if output:
        output.write_text(result, encoding="utf-8")
        rprint(f"\n[green]✓ Result saved to {output}[/green]")
