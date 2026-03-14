#!/usr/bin/env python3
"""
Integration Test Suite for Meeting Management Plugin

Tests the complete workflow of meeting recording in Agent Teams.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks"))


class IntegrationTest:
    """Integration test runner for meeting management."""

    def __init__(self):
        self.test_results = []
        self.meeting_records_dir = PROJECT_ROOT / ".claude" / "docs" / "meeting-records"

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "message": message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   → {message}")

    def test_file_structure(self):
        """Test that all required files exist."""
        required_files = [
            ".claude/agents/meeting-recorder.md",
            ".claude/skills/meeting-record.md",
            ".claude/rules/meeting-auto-recorder.md",
            ".claude/hooks/team-create-add-recorder.py",
            ".claude/hooks/record-message.py",
            ".claude/hooks/generate-meeting-summary.py",
            ".claude/hooks/hooks.json",
        ]

        all_exist = True
        for file_path in required_files:
            full_path = PROJECT_ROOT / file_path
            if not full_path.exists():
                all_exist = False
                self.log_test(f"File exists: {file_path}", False, "File not found")

        self.log_test("File Structure", all_exist)

    def test_hook_configuration(self):
        """Test hook configuration file."""
        hooks_json = PROJECT_ROOT / ".claude" / "hooks" / "hooks.json"
        with open(hooks_json) as f:
            config = json.load(f)

        required_hooks = [
            "team-create-add-recorder.py",
            "record-message.py",
            "generate-meeting-summary.py"
        ]

        # Check if each required hook file is referenced in the hooks list
        hooks_list = config.get("hooks", [])
        all_present = True
        missing_hooks = []

        for required_hook in required_hooks:
            found = False
            for hook in hooks_list:
                command = hook.get("command", "")
                if required_hook in command:
                    found = True
                    break
            if not found:
                all_present = False
                missing_hooks.append(required_hook)

        message = f"Missing hooks: {', '.join(missing_hooks)}" if missing_hooks else ""
        self.log_test("Hook Configuration", all_present, message)

    def test_agent_definition(self):
        """Test meeting-recorder agent definition."""
        agent_file = PROJECT_ROOT / ".claude" / "agents" / "meeting-recorder.md"
        with open(agent_file) as f:
            content = f.read()

        # Check for actual sections in the file
        required_sections = [
            "Core Mission",
            "Meeting Recording Workflow",
            "Frontmatter Structure"
        ]
        all_present = all(section in content for section in required_sections)
        self.log_test("Agent Definition", all_present)

    def test_skill_definition(self):
        """Test meeting-record skill definition."""
        skill_file = PROJECT_ROOT / ".claude" / "skills" / "meeting-record.md"
        with open(skill_file) as f:
            content = f.read()

        required_commands = [
            "/meeting-start",
            "/meeting-end",
            "/meeting-list",
            "/meeting-search",
            "/meeting-summary",
            "/meeting-actions"
        ]
        all_present = all(cmd in content for cmd in required_commands)
        self.log_test("Skill Definition", all_present)

    def test_rule_definition(self):
        """Test meeting-auto-recorder rule."""
        rule_file = PROJECT_ROOT / ".claude" / "rules" / "meeting-auto-recorder.md"
        with open(rule_file) as f:
            content = f.read()

        has_paths = "---" in content and "paths:" in content
        has_requirement = "MUST include meeting-recorder" in content
        self.log_test("Rule Definition", has_paths and has_requirement)

    def test_meeting_records_directory(self):
        """Test meeting records directory structure."""
        if not self.meeting_records_dir.exists():
            self.meeting_records_dir.mkdir(parents=True)

        # Create sample transcript with new naming convention
        date_str = datetime.now().strftime('%Y-%m-%d')
        transcript_file = self.meeting_records_dir / f"{date_str}-001-api-design.md"
        transcript_file.write_text(
            "# Meeting Transcript\n\n"
            f"**Meeting ID:** {date_str}-001\n"
            f"**Team:** test-team\n"
            f"**Topic:** api-design\n"
            f"**Date:** {date_str}\n"
            f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "---\n\n"
            "### [10:00:00] agent1 → team-lead\n\n"
            "Test message from agent1 about API design\n"
        )

        self.log_test("Meeting Records Directory", transcript_file.exists())

    def test_hook_syntax(self):
        """Test Python hook scripts for syntax errors."""
        hook_files = [
            ".claude/hooks/team-create-add-recorder.py",
            ".claude/hooks/record-message.py",
            ".claude/hooks/generate-meeting-summary.py",
        ]

        all_valid = True
        for hook_file in hook_files:
            hook_path = PROJECT_ROOT / hook_file
            try:
                with open(hook_path) as f:
                    compile(f.read(), hook_path, "exec")
            except SyntaxError as e:
                all_valid = False
                self.log_test(f"Hook Syntax: {hook_file}", False, str(e))

        self.log_test("Hook Scripts Syntax", all_valid)

    def generate_report(self):
        """Generate test report."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed

        print("\n" + "=" * 60)
        print("INTEGRATION TEST REPORT")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("=" * 60)

        # Generate markdown report
        report_path = PROJECT_ROOT / "test-report.md"
        with open(report_path, "w") as f:
            f.write("# Meeting Management - Integration Test Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Tests**: {total}\n")
            f.write(f"- **Passed**: {passed} ✅\n")
            f.write(f"- **Failed**: {failed} ❌\n")
            f.write(f"- **Success Rate**: {passed/total*100:.1f}%\n\n")
            f.write("## Test Results\n\n")
            f.write("| Test | Status | Notes |\n")
            f.write("|------|--------|-------|\n")
            for result in self.test_results:
                status = "✅" if result["passed"] else "❌"
                notes = result["message"] or "-"
                f.write(f"| {result['name']} | {status} | {notes} |\n")

        print(f"\n📄 Report saved to: {report_path}")

    def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 Running Integration Tests...\n")

        self.test_file_structure()
        self.test_hook_configuration()
        self.test_agent_definition()
        self.test_skill_definition()
        self.test_rule_definition()
        self.test_meeting_records_directory()
        self.test_hook_syntax()

        self.generate_report()

        return all(r["passed"] for r in self.test_results)


if __name__ == "__main__":
    tester = IntegrationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
