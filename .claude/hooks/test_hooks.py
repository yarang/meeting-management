#!/usr/bin/env python3
"""
Test script for meeting management hooks
Validates hook functionality with sample data
"""

import json
import subprocess
import os
import tempfile
from datetime import datetime

def test_team_create_hook():
    """Test team creation hook"""
    print("Testing team-create-add-recorder.py...")

    input_data = {
        "team_name": "test-team",
        "members": ["agent1", "agent2"],
        "event": "SubagentStart"
    }

    result = subprocess.run(
        ["python3", ".claude/hooks/team-create-add-recorder.py"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )

    print(f"Exit Code: {result.returncode}")
    print(f"Stdout: {result.stdout}")

    if result.returncode == 0:
        try:
            output = json.loads(result.stdout.strip().split('\n')[-1])
            print(f"Parsed Output: {json.dumps(output, indent=2)}")

            if "meeting-recorder" in output.get("members", []):
                print("✓ Test PASSED: meeting-recorder added to team")
                return True
            else:
                print("✗ Test FAILED: meeting-recorder not found in members")
                return False
        except Exception as e:
            print(f"✗ Test FAILED: Could not parse output - {e}")
            return False
    else:
        print(f"✗ Test FAILED: {result.stderr}")
        return False

def test_record_message_hook():
    """Test message recording hook"""
    print("\nTesting record-message.py...")

    input_data = {
        "team_name": "test-team",
        "from": "agent1",
        "to": "agent2",
        "type": "message",
        "content": "This is a test message for the transcript",
        "timestamp": datetime.now().isoformat()
    }

    result = subprocess.run(
        ["python3", ".claude/hooks/record-message.py"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )

    print(f"Exit Code: {result.returncode}")
    print(f"Stdout: {result.stdout}")

    if result.returncode == 0:
        try:
            output = json.loads(result.stdout.strip().split('\n')[-1])

            transcript_path = output.get("transcript", "")
            if os.path.exists(transcript_path):
                print(f"✓ Test PASSED: Transcript created at {transcript_path}")

                # Verify content
                with open(transcript_path, 'r') as f:
                    content = f.read()
                    if "test message" in content:
                        print("✓ Test PASSED: Message content found in transcript")
                        return True
                    else:
                        print("✗ Test FAILED: Message content not found in transcript")
                        return False
            else:
                print(f"✗ Test FAILED: Transcript not created at {transcript_path}")
                return False
        except Exception as e:
            print(f"✗ Test FAILED: Could not parse output - {e}")
            return False
    else:
        print(f"✗ Test FAILED: {result.stderr}")
        return False

def test_generate_summary_hook():
    """Test meeting summary generation hook"""
    print("\nTesting generate-meeting-summary.py...")

    # First, create a test transcript
    date_str = datetime.now().strftime("%Y-%m-%d")
    test_transcript = f"""# Meeting Transcript: test-team

**Date:** {date_str}
**Started:** 2025-01-09 10:00:00

---

### [10:00:00] agent1 → team

Let's discuss the project requirements.

### [10:00:30] agent2 → agent1

I agree. We need to define the action items.

### [10:01:00] agent1 → team

Action item: agent2 will complete the design by Friday.

### [10:01:30] agent2 → team

Acknowledged. I'll handle that task.

### [10:02:00] agent1 → team

Meeting concluded. Great work everyone.
"""

    # Create temporary transcript
    records_dir = os.path.join(os.getcwd(), "meeting-records", "test-team")
    os.makedirs(records_dir, exist_ok=True)
    transcript_path = os.path.join(records_dir, f"{date_str}.md")

    with open(transcript_path, 'w') as f:
        f.write(test_transcript)

    print(f"Created test transcript at: {transcript_path}")

    # Test the summary hook
    input_data = {
        "team_name": "test-team",
        "event": "SubagentStop",
        "transcript_path": transcript_path
    }

    result = subprocess.run(
        ["python3", ".claude/hooks/generate-meeting-summary.py"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )

    print(f"Exit Code: {result.returncode}")
    print(f"Stdout: {result.stdout}")

    if result.returncode == 0:
        try:
            output = json.loads(result.stdout.strip().split('\n')[-1])
            print(f"Parsed Output: {json.dumps(output, indent=2)}")

            summary_path = output.get("summary_path", "")
            if os.path.exists(summary_path):
                print(f"✓ Test PASSED: Summary created at {summary_path}")

                # Verify content
                with open(summary_path, 'r') as f:
                    content = f.read()
                    if "Action Items" in content and "agent2" in content:
                        print("✓ Test PASSED: Summary contains action items")
                        return True
                    else:
                        print("✗ Test FAILED: Summary missing expected content")
                        return False
            else:
                print(f"✗ Test FAILED: Summary not created at {summary_path}")
                return False
        except Exception as e:
            print(f"✗ Test FAILED: Could not parse output - {e}")
            return False
    else:
        print(f"✗ Test FAILED: {result.stderr}")
        return False

def main():
    """Run all hook tests"""
    print("=" * 60)
    print("Meeting Management Hooks Test Suite")
    print("=" * 60)

    results = {
        "team_create": test_team_create_hook(),
        "record_message": test_record_message_hook(),
        "generate_summary": test_generate_summary_hook()
    }

    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")

    all_passed = all(results.values())

    print("=" * 60)

    if all_passed:
        print("✓ All tests PASSED")
        return 0
    else:
        print("✗ Some tests FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
