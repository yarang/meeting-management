#!/usr/bin/env python3
"""
Meeting Management Plugin Setup Script

Installs the plugin by configuring Claude Code hooks.
"""

import json
import os
import sys
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent


def get_claude_settings_path():
    """Get the Claude Code settings.json path."""
    home = Path.home()
    return home / ".claude" / "settings.json"


def get_claude_settings_original_path():
    """Get the path for original settings backup."""
    return get_claude_settings_path().with_suffix(".json.original")


def backup_current_settings():
    """Backup current Claude Code settings."""
    settings_path = get_claude_settings_path()
    backup_path = get_claude_settings_original_path()

    if settings_path.exists():
        import shutil
        shutil.copy(settings_path, backup_path)
        print(f"✅ Backed up current settings to: {backup_path}")
        return True
    return False


def restore_original_settings():
    """Restore original settings from backup."""
    settings_path = get_claude_settings_path()
    backup_path = get_claude_settings_original_path()

    if backup_path.exists():
        import shutil
        shutil.copy(backup_path, settings_path)
        print(f"✅ Restored original settings from: {backup_path}")
        return True
    print("⚠️  No backup found to restore")
    return False


def install_hooks():
    """Install meeting-management hooks to Claude Code settings."""
    project_root = get_project_root()
    settings_path = get_claude_settings_path()

    # Read current settings
    if settings_path.exists():
        with open(settings_path) as f:
            settings = json.load(f)
    else:
        settings = {}

    # Initialize hooks if not exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    # Define meeting-management hooks
    hooks_config = {
        "SubagentStart": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 .claude/hooks/team-create-add-recorder.py",
                        "timeout": 10
                    }
                ]
            }
        ],
        "Notification": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 .claude/hooks/record-message.py",
                        "timeout": 10
                    }
                ]
            }
        ],
        "SubagentStop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 .claude/hooks/generate-meeting-summary.py",
                        "timeout": 10
                    }
                ]
            }
        ]
    }

    # Add hooks to settings (merge with existing)
    for event, hooks in hooks_config.items():
        if event not in settings["hooks"]:
            settings["hooks"][event] = []
        settings["hooks"][event].extend(hooks)

    # Write updated settings
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    print(f"✅ Installed hooks to: {settings_path}")
    return True


def uninstall_hooks():
    """Remove meeting-management hooks from Claude Code settings."""
    settings_path = get_claude_settings_path()

    if not settings_path.exists():
        print("⚠️  Settings file not found")
        return False

    with open(settings_path) as f:
        settings = json.load(f)

    if "hooks" not in settings:
        print("⚠️  No hooks found in settings")
        return False

    # Remove meeting-management hooks
    removed = False
    for event in ["SubagentStart", "Notification", "SubagentStop"]:
        if event in settings["hooks"]:
            # Filter out meeting-management hooks
            original_count = len(settings["hooks"][event])
            settings["hooks"][event] = [
                h for h in settings["hooks"][event]
                if not any(
                    "team-create-add-recorder" in hook.get("command", "") or
                    "record-message" in hook.get("command", "") or
                    "generate-meeting-summary" in hook.get("command", "")
                    for hook in h.get("hooks", [])
                )
            ]
            if len(settings["hooks"][event]) < original_count:
                removed = True

    if removed:
        # Write updated settings
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)
        print(f"✅ Removed hooks from: {settings_path}")
    else:
        print("⚠️  No meeting-management hooks found")

    return removed


def print_usage():
    """Print usage instructions."""
    print("""
🤖 MoAI Meeting Management Plugin

Usage:
    python setup.py [command]

Commands:
    install     Install hooks to Claude Code settings
    uninstall   Remove hooks from Claude Code settings
    restore     Restore original settings from backup
    status      Show current installation status
    help        Show this help message

Examples:
    python setup.py install
    python setup.py uninstall
    python setup.py status
    """)


def print_status():
    """Print current installation status."""
    project_root = get_project_root()
    settings_path = get_claude_settings_path()

    print("📊 Installation Status")
    print("=" * 50)

    # Check project files
    print("\n📁 Project Files:")
    required_files = [
        ".claude/agents/meeting-recorder.md",
        ".claude/skills/meeting-record.md",
        ".claude/rules/meeting-auto-recorder.md",
        ".claude/hooks/team-create-add-recorder.py",
        ".claude/hooks/record-message.py",
        ".claude/hooks/generate-meeting-summary.py",
    ]

    for file_path in required_files:
        full_path = project_root / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"  {status} {file_path}")

    # Check hooks in settings
    print("\n🔗 Claude Code Hooks:")
    if settings_path.exists():
        with open(settings_path) as f:
            settings = json.load(f)

        if "hooks" in settings:
            hooks = settings["hooks"]
            hook_events = {
                "SubagentStart": "team-create-add-recorder.py",
                "Notification": "record-message.py",
                "SubagentStop": "generate-meeting-summary.py"
            }

            for event, hook_file in hook_events.items():
                installed = any(
                    hook_file in str(h)
                    for h in hooks.get(event, [])
                    for hook in h.get("hooks", [])
                )
                status = "✅" if installed else "❌"
                print(f"  {status} {event}")
        else:
            print("  ⚠️  No hooks configured")
    else:
        print("  ⚠️  Settings file not found")

    # Check backup
    print("\n💾 Backup:")
    backup_path = get_claude_settings_original_path()
    if backup_path.exists():
        print(f"  ✅ {backup_path}")
    else:
        print("  ⚠️  No backup found")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "install":
        backup_current_settings()
        install_hooks()
        print("\n✅ Installation complete!")
        print("\nTo use the plugin:")
        print("  1. Restart Claude Code")
        print("  2. Create a team: TeamCreate team_name=\"my-project\"")
        print("  3. The meeting-recorder agent will be added automatically")

    elif command == "uninstall":
        uninstall_hooks()
        print("\n✅ Uninstallation complete!")

    elif command == "restore":
        restore_original_settings()
        print("\n✅ Restore complete!")

    elif command == "status":
        print_status()

    elif command == "help" or command == "--help" or command == "-h":
        print_usage()

    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
