import sys
import shutil
import subprocess
from pathlib import Path
import typer
import keyring
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from devpilot.core.skills import SkillLoader
from devpilot.core.claude import ClaudeClient

app = typer.Typer(
    help="skillpilot — 228 AI skills for Claude Code\n\nInstall, run and manage AI skills directly in your Claude Code workflow.",
    no_args_is_help=True,
)
console = Console()
KEYRING_SERVICE = "skillpilot"
CLAUDE_COMMANDS_DIR = Path.home() / ".claude" / "commands"


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_api_key() -> str | None:
    return keyring.get_password(KEYRING_SERVICE, "api_key")


def _claude_dir_ok() -> bool:
    try:
        CLAUDE_COMMANDS_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


# ── commands ─────────────────────────────────────────────────────────────────

@app.command()
def init():
    """Configure ta clé API Anthropic pour skillpilot run."""
    api_key = typer.prompt("Clé API Anthropic (sk-ant-...)", hide_input=True)
    keyring.set_password(KEYRING_SERVICE, "api_key", api_key)
    rprint("[green]✓ Clé API sauvegardée.[/green]")


@app.command(name="list")
def list_skills(
    category: str = typer.Option(None, "--category", "-c", help="Filtrer par catégorie"),
):
    """Liste les 228 skills disponibles, par catégorie."""
    loader = SkillLoader()

    if category:
        skills = loader.list_category(category)
        if not skills:
            rprint(f"[red]Catégorie '{category}' introuvable.[/red]")
            raise typer.Exit(1)
        table = Table(title=f"skillpilot — {category} ({len(skills)} skills)")
        table.add_column("Skill", style="cyan")
        for s in skills:
            table.add_row(s)
        console.print(table)
        return

    all_data = loader.list_all()
    total = sum(len(v["skills"]) for v in all_data.values())
    table = Table(title=f"skillpilot — {total} AI skills pour Claude Code")
    table.add_column("Catégorie", style="cyan")
    table.add_column("Skills", justify="right", style="green")
    for cat, info in sorted(all_data.items()):
        table.add_row(cat, str(len(info["skills"])))
    console.print(table)
    rprint("\n[dim]skillpilot install <skill>  →  installe dans Claude Code[/dim]")
    rprint("[dim]skillpilot run <skill>      →  exécute via API Anthropic[/dim]")


@app.command()
def search(keyword: str = typer.Argument(..., help="Mot-clé à chercher")):
    """Cherche un skill par mot-clé dans toutes les catégories."""
    loader = SkillLoader()
    results = loader.search(keyword)
    if not results:
        rprint(f"[yellow]Aucun skill trouvé pour '{keyword}'[/yellow]")
        raise typer.Exit(1)
    table = Table(title=f"{len(results)} résultat(s) pour '{keyword}'")
    table.add_column("Skill", style="cyan")
    table.add_column("Catégorie", style="magenta")
    for r in results:
        table.add_row(r["skill"], r["category"])
    console.print(table)


@app.command()
def info(skill: str = typer.Argument(..., help="Nom du skill")):
    """Affiche le contenu d'un skill (20 premières lignes)."""
    loader = SkillLoader()
    result = loader.find(skill)
    if not result:
        rprint(f"[red]✗ Skill '{skill}' introuvable. Lance: skillpilot search {skill}[/red]")
        raise typer.Exit(1)
    cat, path = result
    lines = path.read_text(encoding="utf-8").split("\n")[:20]
    console.rule(f"[bold cyan]{skill}[/bold cyan] [dim]({cat})[/dim]")
    console.print("\n".join(lines))
    console.rule()
    rprint(f"\n[dim]skillpilot install {skill}  →  installer dans Claude Code[/dim]")
    rprint(f"[dim]skillpilot run {skill}      →  exécuter maintenant[/dim]")


@app.command()
def install(
    skill: str = typer.Argument(..., help="Nom du skill à installer dans Claude Code"),
    category: str = typer.Option(None, "--category", "-c", help="Catégorie du skill"),
):
    """Installe un skill dans Claude Code (~/.claude/commands/)."""
    loader = SkillLoader()
    try:
        content = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    if not _claude_dir_ok():
        rprint("[red]✗ Impossible de créer ~/.claude/commands/. Claude Code est-il installé ?[/red]")
        raise typer.Exit(1)

    dest = CLAUDE_COMMANDS_DIR / f"{skill}.md"
    dest.write_text(content, encoding="utf-8")
    rprint(f"[green]✓ '{skill}' installé dans Claude Code.[/green]")
    rprint(f"[dim]Chemin : {dest}[/dim]")
    rprint(f"[dim]Utilise /{skill} dans Claude Code pour l'activer.[/dim]")


@app.command(name="install-all")
def install_all(
    category: str = typer.Option(None, "--category", "-c", help="Installer une catégorie entière"),
):
    """Installe tous les skills (ou une catégorie) dans Claude Code."""
    loader = SkillLoader()

    if not _claude_dir_ok():
        rprint("[red]✗ Impossible de créer ~/.claude/commands/.[/red]")
        raise typer.Exit(1)

    cats = [category] if category else loader.categories()
    total = 0
    for cat in cats:
        for skill_name in loader.list_category(cat):
            try:
                content = loader.load(skill_name, category=cat)
                dest = CLAUDE_COMMANDS_DIR / f"{skill_name}.md"
                dest.write_text(content, encoding="utf-8")
                total += 1
            except Exception:
                pass

    rprint(f"[green]✓ {total} skills installés dans {CLAUDE_COMMANDS_DIR}[/green]")
    rprint("[dim]Redémarre Claude Code pour les voir disponibles.[/dim]")


@app.command()
def copy(
    skill: str = typer.Argument(..., help="Nom du skill à copier dans le clipboard"),
    category: str = typer.Option(None, "--category", "-c"),
):
    """Copie le contenu d'un skill dans le clipboard."""
    loader = SkillLoader()
    try:
        content = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    try:
        if sys.platform == "win32":
            subprocess.run("clip", input=content.encode("utf-16"), check=True)
        elif sys.platform == "darwin":
            subprocess.run("pbcopy", input=content.encode(), check=True)
        else:
            subprocess.run(["xclip", "-selection", "clipboard"], input=content.encode(), check=True)
        rprint(f"[green]✓ '{skill}' copié dans le clipboard.[/green]")
        rprint("[dim]Colle-le directement dans Claude Code ou Claude.ai.[/dim]")
    except Exception:
        rprint("[yellow]Clipboard non disponible. Contenu affiché ci-dessous :[/yellow]\n")
        console.print(content)


@app.command()
def run(
    skill: str = typer.Argument(..., help="Nom du skill à exécuter"),
    category: str = typer.Option(None, "--category", "-c", help="Catégorie du skill"),
    input_text: str = typer.Option(None, "--input", "-i", help="Code ou texte à analyser"),
):
    """Exécute un skill via l'API Anthropic (nécessite skillpilot init)."""
    api_key = _get_api_key()
    if not api_key:
        rprint("[red]✗ Pas de clé API. Lance d'abord: skillpilot init[/red]")
        raise typer.Exit(1)

    loader = SkillLoader()
    try:
        prompt = loader.load(skill, category=category)
    except ValueError as e:
        rprint(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    if not input_text:
        rprint("[yellow]Colle ton code/texte (Ctrl+D pour terminer):[/yellow]")
        input_text = sys.stdin.read()

    with console.status(f"[bold green]Exécution de '{skill}' via Claude..."):
        result = ClaudeClient(api_key=api_key).run(skill_prompt=prompt, user_input=input_text)

    console.rule(f"[bold]Résultat — {skill}[/bold]")
    console.print(result)
    console.rule()
