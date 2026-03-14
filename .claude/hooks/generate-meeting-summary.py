#!/usr/bin/env python3
"""
Hook: Meeting Summary Generation
Trigger: On team shutdown (TeamDelete or member shutdown)
Purpose: Generate final meeting summary with action items
"""

import json
import sys
import os
import re
import glob
from datetime import datetime
from collections import defaultdict

# Configuration
RECORDS_DIR = ".claude/docs/meeting-records"


def find_latest_transcript(team_name: str) -> str:
    """
    Find the latest transcript file for a team.

    Args:
        team_name: Name of the team

    Returns:
        Path to the latest transcript file or None
    """
    records_dir = os.path.join(os.getcwd(), RECORDS_DIR)

    if not os.path.exists(records_dir):
        return None

    # Find all transcript files matching pattern
    pattern = os.path.join(records_dir, "*.md")
    files = glob.glob(pattern)

    # Filter out summary files
    transcript_files = [f for f in files if not f.endswith("-summary.md")]

    if not transcript_files:
        return None

    # Sort by modification time, get latest
    latest = max(transcript_files, key=os.path.getmtime)
    return latest


def extract_meeting_id(transcript_path: str) -> str:
    """
    Extract meeting ID from transcript filename.

    Args:
        transcript_path: Path to transcript file

    Returns:
        Meeting ID string (e.g., "2026-03-15-001-api-design")
    """
    filename = os.path.basename(transcript_path)
    # Remove .md extension
    return filename.replace(".md", "")


def extract_participants(transcript_content: str) -> list:
    """
    Extract list of unique participants from transcript.

    Args:
        transcript_content: Full transcript text

    Returns:
        List of participant names
    """
    # Find all message senders
    pattern = r'\[(?:\d{2}:\d{2}:\d{2})\] (\w+) →'
    participants = set(re.findall(pattern, transcript_content))

    # Remove "team" if present (not a real participant)
    participants.discard("team")

    return sorted(list(participants))


def extract_messages(transcript_content: str) -> list:
    """
    Extract individual messages from transcript.

    Args:
        transcript_content: Full transcript text

    Returns:
        List of message dictionaries
    """
    messages = []

    # Split by message headers
    pattern = r'### \[(\d{2}:\d{2}:\d{2})\] (\w+) → ([\w-]+)\n\n(.*?)(?=\n### \[\d{2}:\d{2}:\d{2}\]|\Z)'
    matches = re.findall(pattern, transcript_content, re.DOTALL)

    for time_str, from_agent, to_agent, content in matches:
        # Clean up content
        content = content.strip()

        # Remove code block markers if present
        if content.startswith("```"):
            lines = content.split('\n')
            if len(lines) > 2:
                content = '\n'.join(lines[1:-1])

        messages.append({
            "time": time_str,
            "from": from_agent,
            "to": to_agent,
            "content": content
        })

    return messages


def identify_action_items(messages: list) -> list:
    """
    Identify action items from messages.

    Args:
        messages: List of message dictionaries

    Returns:
        List of action item dictionaries
    """
    action_items = []

    # Action item indicators
    action_keywords = [
        r'action\s+item',
        r'to\s+do',
        r'task',
        r'assign',
        r'responsible',
        r'follow\s+up',
        r'next\s+step',
        r'deadline',
        r'complete\s+by',
        r'구현',  # Korean: implement
        r'수정',  # Korean: modify
        r'추가',  # Korean: add
        r'확인',  # Korean: check
    ]

    # Combine patterns
    pattern = r'\b(' + '|'.join(action_keywords) + r')\b'

    for msg in messages:
        content_lower = msg["content"].lower()

        if re.search(pattern, content_lower):
            # Extract potential assignee (mentions of agent names)
            assignee = None

            # Look for "assigned to X" or "X will do" patterns
            assignee_patterns = [
                r'assigned to (\w+)',
                r'(\w+) will',
                r'(\w+) to handle',
                r'(\w+) responsible',
                r'담당:\s*(\w+)',  # Korean
                r'(\w+)\s+담당',  # Korean
            ]

            for ap in assignee_patterns:
                match = re.search(ap, content_lower)
                if match:
                    assignee = match.group(1).capitalize()
                    break

            if not assignee:
                assignee = msg["from"]  # Default to sender

            action_items.append({
                "time": msg["time"],
                "assignee": assignee,
                "description": msg["content"],
                "source": msg["from"]
            })

    return action_items


def generate_summary(transcript_path: str) -> dict:
    """
    Generate meeting summary from transcript.

    Args:
        transcript_path: Path to the transcript file

    Returns:
        Dictionary containing summary data
    """
    try:
        with open(transcript_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return {
            "error": f"Transcript not found: {transcript_path}"
        }

    # Extract metadata
    meeting_id_match = re.search(r'\*\*Meeting ID:\*\* (.+)', content)
    team_match = re.search(r'\*\*Team:\*\* (.+)', content)
    topic_match = re.search(r'\*\*Topic:\*\* (.+)', content)
    date_match = re.search(r'\*\*Date:\*\* (.+)', content)

    meeting_id = meeting_id_match.group(1) if meeting_id_match else extract_meeting_id(transcript_path)
    team_name = team_match.group(1) if team_match else "Unknown Team"
    topic = topic_match.group(1) if topic_match else "general"
    date = date_match.group(1) if date_match else "Unknown Date"

    # Extract participants
    participants = extract_participants(content)

    # Extract messages
    messages = extract_messages(content)

    # Identify action items
    action_items = identify_action_items(messages)

    # Generate discussion summary (first and last few messages)
    discussion_summary = []

    if messages:
        # First message
        if len(messages) > 0:
            discussion_summary.append({
                "phase": "Opening",
                "summary": f"Meeting initiated by {messages[0]['from']}"
            })

        # Middle messages (sample if too many)
        middle_messages = messages[1:-1] if len(messages) > 2 else []
        if middle_messages:
            sample_size = min(3, len(middle_messages))
            step = len(middle_messages) // sample_size if sample_size > 0 else 1

            for i in range(0, len(middle_messages), step):
                msg = middle_messages[i]
                discussion_summary.append({
                    "phase": "Discussion",
                    "summary": f"{msg['from']}: {msg['content'][:100]}..."
                })

        # Last message
        if len(messages) > 1:
            discussion_summary.append({
                "phase": "Closing",
                "summary": f"Meeting concluded by {messages[-1]['from']}"
            })

    # Compile summary
    summary = {
        "meeting_id": meeting_id,
        "team_name": team_name,
        "topic": topic,
        "date": date,
        "participants": participants,
        "participant_count": len(participants),
        "message_count": len(messages),
        "discussion_summary": discussion_summary,
        "action_items": action_items,
        "action_item_count": len(action_items),
        "transcript_path": transcript_path
    }

    return summary


def format_summary_markdown(summary: dict) -> str:
    """
    Format summary as markdown.

    Args:
        summary: Summary dictionary

    Returns:
        Formatted markdown string
    """
    md = f"# Meeting Summary\n\n"
    md += f"**Meeting ID:** {summary['meeting_id']}\n"
    md += f"**Team:** {summary['team_name']}\n"
    md += f"**Topic:** {summary['topic']}\n"
    md += f"**Date:** {summary['date']}\n"
    md += f"**Participants:** {summary['participant_count']} ({', '.join(summary['participants'])})\n"
    md += f"**Messages:** {summary['message_count']}\n"
    md += f"**Action Items:** {summary['action_item_count']}\n\n"

    md += "---\n\n"

    # Discussion Summary
    md += "## Discussion Summary\n\n"

    if summary.get("discussion_summary"):
        for item in summary["discussion_summary"]:
            md += f"### {item['phase']}\n"
            md += f"{item['summary']}\n\n"
    else:
        md += "No discussion details available.\n\n"

    # Action Items
    md += "## Action Items\n\n"

    if summary.get("action_items"):
        for i, item in enumerate(summary["action_items"], 1):
            md += f"### {i}. {item['description'][:80]}...\n\n"
            md += f"- **Assignee:** {item['assignee']}\n"
            md += f"- **Source:** {item['source']}\n"
            md += f"- **Time:** {item['time']}\n\n"
    else:
        md += "No action items identified.\n\n"

    # Next Steps
    md += "## Next Steps\n\n"

    if summary.get("action_items"):
        md += "1. Review and prioritize action items\n"
        md += f"2. Assign deadlines to {summary['action_item_count']} action items\n"
        md += "3. Schedule follow-up meeting if needed\n"
        md += "4. Update project tracking system\n\n"
    else:
        md += "1. Review meeting outcomes\n"
        md += "2. Determine if follow-up actions are needed\n\n"

    # Metadata
    md += "---\n\n"
    md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md += f"**Transcript:** {summary['transcript_path']}\n"

    return md


def main():
    """
    Read team shutdown event from stdin and generate summary.

    Expected JSON input:
    {
        "team_name": "team-name",
        "event": "TeamDelete" | "TeamShutdown",
        "transcript_path": "optional/path/to/transcript"
    }
    """
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())

        team_name = input_data.get("team_name", "")

        if not team_name:
            print("Error: team_name is required", file=sys.stderr)
            sys.exit(1)

        # Get transcript path
        transcript_path = input_data.get("transcript_path")

        if not transcript_path:
            # Find latest transcript
            transcript_path = find_latest_transcript(team_name)

        # Check if transcript exists
        if not transcript_path or not os.path.exists(transcript_path):
            print(f"Warning: No transcript found for team '{team_name}'", file=sys.stderr)
            output = {
                "status": "skipped",
                "team_name": team_name,
                "message": "No transcript found to summarize"
            }
            print(json.dumps(output))
            sys.exit(0)

        # Generate summary
        summary = generate_summary(transcript_path)

        if "error" in summary:
            print(f"Error: {summary['error']}", file=sys.stderr)
            sys.exit(1)

        # Format as markdown
        summary_md = format_summary_markdown(summary)

        # Write summary file: YYYY-MM-DD-NNN-summary.md
        records_dir = os.path.join(os.getcwd(), RECORDS_DIR)
        os.makedirs(records_dir, exist_ok=True)

        # Extract meeting ID from transcript path
        meeting_id = extract_meeting_id(transcript_path)
        summary_filename = f"{meeting_id}-summary.md"
        summary_path = os.path.join(records_dir, summary_filename)

        with open(summary_path, 'w') as f:
            f.write(summary_md)

        output = {
            "status": "success",
            "team_name": team_name,
            "meeting_id": summary["meeting_id"],
            "summary_path": summary_path,
            "participants": summary["participant_count"],
            "action_items": summary["action_item_count"],
            "message_count": summary["message_count"],
            "message": f"Summary generated: {summary_filename}"
        }
        print(json.dumps(output))

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
