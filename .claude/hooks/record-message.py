#!/usr/bin/env python3
"""
Hook: Message Recording
Trigger: On every SendMessage in team context
Purpose: Log messages to current meeting transcript
"""

import json
import sys
import os
import re
from datetime import datetime
import fcntl

# Configuration
RECORDS_DIR = ".claude/docs/meeting-records"
SEQUENCE_FILE = ".claude/docs/meeting-records/.sequence"


def get_next_sequence_number() -> int:
    """Get the next sequence number for today's meetings."""
    os.makedirs(os.path.dirname(SEQUENCE_FILE), exist_ok=True)

    if os.path.exists(SEQUENCE_FILE):
        with open(SEQUENCE_FILE, 'r') as f:
            try:
                return int(f.read().strip()) + 1
            except:
                return 1
    return 1


def save_sequence_number(seq: int) -> None:
    """Save the current sequence number."""
    os.makedirs(os.path.dirname(SEQUENCE_FILE), exist_ok=True)
    with open(SEQUENCE_FILE, 'w') as f:
        f.write(str(seq))


def extract_topic(messages: list) -> str:
    """
    Extract topic from message content using keyword detection.

    Args:
        messages: List of message dictionaries

    Returns:
        Detected topic or default
    """
    # Topic detection keywords
    topic_keywords = {
        "api-design": ["api", "endpoint", "rest", "graphql", "interface"],
        "database": ["database", "schema", "migration", "query", "sql"],
        "auth": ["auth", "login", "permission", "security", "token"],
        "frontend": ["ui", "frontend", "component", "react", "vue"],
        "backend": ["backend", "server", "service", "microservice"],
        "testing": ["test", "testing", "coverage", "pytest", "unit"],
        "deployment": ["deploy", "release", "ci/cd", "build", "docker"],
        "planning": ["plan", "sprint", "backlog", "estimate", "task"],
        "bug": ["bug", "fix", "issue", "error", "problem"],
        "review": ["review", "pr", "code review", "pull request"],
    }

    # Count keyword matches
    topic_scores = {}
    for msg in messages:
        content = msg.get("content", "").lower()
        for topic, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in content)
            if score > 0:
                topic_scores[topic] = topic_scores.get(topic, 0) + score

    # Return topic with highest score or default
    if topic_scores:
        return max(topic_scores.items(), key=lambda x: x[1])[0]

    return "general"


def get_transcript_path(team_name: str, date: str = None, topic: str = None) -> tuple:
    """
    Get the transcript file path with sequence number.

    Args:
        team_name: Name of the team
        date: Date string in YYYY-MM-DD format (defaults to today)
        topic: Topic string for filename

    Returns:
        Tuple of (transcript_path, sequence_number)
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Get sequence number
    seq = get_next_sequence_number()

    # Sanitize topic for filename
    if topic is None:
        topic = "general"
    topic_safe = re.sub(r'[^\w\-]', '_', topic.lower())

    # Create meeting-records directory
    records_dir = os.path.join(os.getcwd(), RECORDS_DIR)
    os.makedirs(records_dir, exist_ok=True)

    # File path: YYYY-MM-DD-NNN-topic.md
    filename = f"{date}-{seq:03d}-{topic_safe}.md"
    return os.path.join(records_dir, filename), seq


def format_message_entry(message_data: dict) -> str:
    """
    Format a message entry for the transcript.

    Args:
        message_data: Dictionary containing message information

    Returns:
        Formatted markdown string
    """
    timestamp = message_data.get("timestamp", datetime.now().isoformat())
    from_agent = message_data.get("from", "unknown")
    to_agent = message_data.get("to", "team")
    message_type = message_data.get("type", "message")
    content = message_data.get("content", "")

    # Parse timestamp for readable format
    try:
        dt = datetime.fromisoformat(timestamp)
        time_str = dt.strftime("%H:%M:%S")
    except:
        time_str = timestamp

    entry = f"\n### [{time_str}] {from_agent} → {to_agent}\n\n"

    if message_type != "message":
        entry += f"**Type:** {message_type}\n\n"

    # Format content as code block if it looks like structured data
    if content.startswith("{") or content.startswith("["):
        try:
            json.loads(content)
            entry += f"```\n{content}\n```\n"
        except:
            entry += f"{content}\n"
    else:
        entry += f"{content}\n"

    return entry


def write_to_transcript(transcript_path: str, entry: str) -> None:
    """
    Write an entry to the transcript with file locking for concurrent access.

    Args:
        transcript_path: Path to the transcript file
        entry: Formatted entry to append
    """
    try:
        # Open file in append mode with exclusive lock
        with open(transcript_path, 'a') as f:
            # Acquire exclusive lock (non-blocking)
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)

            try:
                # Write entry
                f.write(entry)
                f.flush()
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    except IOError as e:
        print(f"Warning: Could not acquire lock for {transcript_path} - {e}", file=sys.stderr)
        # Retry once with blocking lock
        with open(transcript_path, 'a') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(entry)
                f.flush()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def initialize_transcript(transcript_path: str, team_name: str, date: str, seq: int, topic: str) -> None:
    """
    Initialize a new transcript file with header if it doesn't exist.

    Args:
        transcript_path: Path to the transcript file
        team_name: Name of the team
        date: Date string for the transcript
        seq: Sequence number
        topic: Meeting topic
    """
    if not os.path.exists(transcript_path):
        header = f"# Meeting Transcript\n\n"
        header += f"**Meeting ID:** {date}-{seq:03d}\n"
        header += f"**Team:** {team_name}\n"
        header += f"**Topic:** {topic}\n"
        header += f"**Date:** {date}\n"
        header += f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        header += "---\n\n"

        with open(transcript_path, 'w') as f:
            f.write(header)


def main():
    """
    Read message event from stdin and append to transcript.

    Expected JSON input:
    {
        "team_name": "team-name",
        "from": "agent-name",
        "to": "recipient-name",
        "type": "message",
        "content": "message content",
        "timestamp": "2025-01-09T10:30:00"
    }
    """
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())

        team_name = input_data.get("team_name", "")

        if not team_name:
            print("Warning: No team_name provided, skipping message recording", file=sys.stderr)
            sys.exit(0)

        # Get current date for transcript
        date_str = datetime.now().strftime("%Y-%m-%d")

        # Get transcript path and save sequence number
        transcript_path, seq = get_transcript_path(team_name, date_str)
        save_sequence_number(seq)

        # Extract topic from messages (simplified - uses current message)
        topic = extract_topic([input_data])

        # Initialize transcript if new
        initialize_transcript(transcript_path, team_name, date_str, seq, topic)

        # Format and write message entry
        entry = format_message_entry(input_data)
        write_to_transcript(transcript_path, entry)

        output = {
            "status": "success",
            "team_name": team_name,
            "transcript": transcript_path,
            "sequence": seq,
            "topic": topic,
            "message": "Message recorded to transcript"
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
