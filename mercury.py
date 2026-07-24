#!/usr/bin/env python3
"""
Mercury - Swift Messenger for Your Repositories

Mercury is the Roman god of messages, travelers, and commerce -- a fitting
patron for a tool whose entire job is ferrying your changes back and forth
between your machine and GitHub.

This is a cross-platform, rich-styled Python tool, originally ported from a
PowerShell git-sync script. It automates:

    fetch -> pull (if behind) -> status -> add -> commit -> push

Requirements:
    pip install rich
"""

import argparse
import os
import subprocess
import sys

try:
    from rich.align import Align
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
except ImportError:
    sys.stderr.write(
        "Mercury needs the 'rich' package for its styled output.\n"
        "Install it with:  pip install rich\n"
    )
    sys.exit(1)


console = Console()

# Generated with pyfiglet (font: ansi_shadow), then embedded so 'rich' is
# the only runtime dependency.
LOGO = r"""
███╗   ███╗███████╗██████╗  ██████╗██╗   ██╗██████╗ ██╗   ██╗
████╗ ████║██╔════╝██╔══██╗██╔════╝██║   ██║██╔══██╗╚██╗ ██╔╝
██╔████╔██║█████╗  ██████╔╝██║     ██║   ██║██████╔╝ ╚████╔╝
██║╚██╔╝██║██╔══╝  ██╔══██╗██║     ██║   ██║██╔══██╗  ╚██╔╝
██║ ╚═╝ ██║███████╗██║  ██║╚██████╗╚██████╔╝██║  ██║   ██║
╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
""".strip("\n")


def display_header() -> None:
    logo = Align.center(Text(LOGO, style="bold bright_yellow"))
    tagline = Align.center(
        Text("🪽  swift messenger for your repositories  🪽", style="italic bright_cyan")
    )
    console.print(
        Panel(
            Group(logo, Text(""), tagline),
            box=box.DOUBLE,
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def section(title: str, icon: str = "➤") -> None:
    """A styled divider announcing the current step."""
    console.rule(f"[bold green]{icon} {title}[/]", style="grey50")


def run_git(args, cwd, capture=False):
    """Run a git command. Returns (returncode, stdout) if capture=True,
    otherwise just the return code (output goes straight to the terminal)."""
    if capture:
        result = subprocess.run(["git"] + args, cwd=cwd, text=True, capture_output=True)
        return result.returncode, result.stdout.strip()
    result = subprocess.run(["git"] + args, cwd=cwd)
    return result.returncode


def parse_args():
    parser = argparse.ArgumentParser(
        prog="mercury",
        description="Mercury - a rich-styled git fetch/pull/add/commit/push assistant.",
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="go",
        choices=["go"],
        help="Action to perform. Currently only 'go' (default) is supported; "
             "reserved so future subcommands can be added without breaking usage.",
    )
    parser.add_argument(
        "--repo",
        default=os.getcwd(),
        help="Path to the git repository (default: current working directory, "
             "i.e. wherever you run the command from).",
    )
    parser.add_argument(
        "--remote-url",
        default=None,
        help=(
            "Expected 'origin' remote URL. If provided, Mercury aborts when the "
            "repo's origin doesn't match. Omit to skip this check."
        ),
    )
    parser.add_argument(
        "--commit-message",
        default="Updates Via Mercury",
        help="Commit message to use (default: 'Updates Via Mercury').",
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for Enter before exiting (useful for CI / automation).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    display_header()

    # Step 0: locate the repository
    section("Locating repository", "📍")
    if not os.path.isdir(args.repo):
        console.print(f"[bold red]ERROR:[/] '{args.repo}' is not a valid directory.")
        return 1
    os.chdir(args.repo)
    console.print(f"[green]✔ Working in:[/] {args.repo}")

    # Step 1: verify the remote (optional)
    if args.remote_url:
        section("Verifying remote repository", "🔎")
        with console.status("[cyan]Checking origin...[/]", spinner="dots"):
            _, remote_url = run_git(["remote", "get-url", "origin"], args.repo, capture=True)
        if remote_url != args.remote_url:
            console.print(
                Panel(
                    f"[bold red]The current repository does not match the expected remote.[/]\n\n"
                    f"[bold]Expected:[/] {args.remote_url}\n"
                    f"[bold]Found:[/]    {remote_url or '(none)'}",
                    title="[bold red]Remote mismatch[/]",
                    border_style="red",
                    box=box.HEAVY,
                )
            )
            if not args.no_wait:
                console.input("[yellow]Press Enter to exit...[/]")
            return 1
        console.print("[bold green]✔ Remote repository matches![/]")

    # Step 2: fetch, then pull if behind
    section("Fetching updates from remote", "📡")
    with console.status("[cyan]Fetching...[/]", spinner="dots"):
        run_git(["fetch"], args.repo)
        _, status_output = run_git(["status"], args.repo, capture=True)

    if "Your branch is behind" in status_output:
        console.print("[bold yellow]⚠ Local repository is behind. Pulling updates...[/]")
        with console.status("[cyan]Pulling...[/]", spinner="dots"):
            run_git(["pull"], args.repo)
    else:
        console.print("[bold green]✔ Local repository is up to date.[/]")

    # Step 3: show local changes
    section("Checking for local changes", "📋")
    subprocess.run(["git", "status"], cwd=args.repo)

    # Step 4: stage everything
    section("Staging changes", "📦")
    with console.status("[cyan]Adding files...[/]", spinner="dots"):
        run_git(["add", "."], args.repo)
    console.print("[bold green]✔ All changes staged.[/]")

    # Step 5: commit
    section("Committing changes", "✍️")
    with console.status("[cyan]Committing...[/]", spinner="dots"):
        rc, commit_output = run_git(["commit", "-m", args.commit_message], args.repo, capture=True)
    if rc == 0:
        console.print(f"[bold green]✔ Committed:[/] {commit_output.splitlines()[0] if commit_output else args.commit_message}")
    else:
        console.print(f"[yellow]⚠ Nothing to commit (or commit failed):[/]\n{commit_output}")

    # Step 6: push
    section("Pushing to remote", "🚀")
    with console.status("[cyan]Pushing...[/]", spinner="dots"):
        rc, push_output = run_git(["push"], args.repo, capture=True)
    if rc == 0:
        console.print("[bold green]✔ Push complete.[/]")
    else:
        console.print(f"[bold red]✘ Push failed:[/]\n{push_output}")

    console.print()
    console.print(
        Panel(
            Align.center("🪽  [bold bright_green]Mercury has delivered your changes![/]  🪽"),
            border_style="bright_yellow",
            box=box.ROUNDED,
        )
    )

    if not args.no_wait:
        console.input("[yellow]Press Enter to close the terminal.[/]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
