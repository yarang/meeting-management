# Meeting Management Hooks

Automatic meeting recording and summary generation for Claude Code teams.

## Overview

These hooks provide automatic meeting recording, transcript generation, and summary creation for team-based workflows in Claude Code.

## Hook Scripts

### 1. Team Creation Hook (`team-create-add-recorder.py`)

**Trigger:** SubagentStart event (when a team is created)

**Purpose:** Automatically adds the `meeting-recorder` agent to new teams

**Features:**
- Detects team creation events
- Adds meeting-recorder agent if not already present
- Updates team configuration
- Provides status feedback

**Expected Input:**
```json
{
  "team_name": "my-team",
  "members": ["agent1", "agent2"],
  "event": "SubagentStart"
}
```

### 2. Message Recording Hook (`record-message.py`)

**Trigger:** Notification event (when SendMessage is called in team context)

**Purpose:** Logs all team messages to daily meeting transcripts

**Features:**
- Records all team communications
- Organizes by team and date
- Markdown-formatted transcripts
- File locking for concurrent access
- Automatic directory creation

**Transcript Location:**
```
meeting-records/{team_name}/{YYYY-MM-DD}.md
```

**Expected Input:**
```json
{
  "team_name": "my-team",
  "from": "agent-name",
  "to": "recipient-name",
  "type": "message",
  "content": "message content",
  "timestamp": "2025-01-09T10:30:00"
}
```

### 3. Meeting Summary Hook (`generate-meeting-summary.py`)

**Trigger:** SubagentStop event (when team shuts down)

**Purpose:** Generates structured meeting summaries with action items

**Features:**
- Extracts participants from transcript
- Identifies action items with assignees
- Creates discussion summary
- Generates next steps
- Outputs formatted markdown

**Summary Location:**
```
meeting-records/{team_name}/{YYYY-MM-DD}-summary.md
```

**Expected Input:**
```json
{
  "team_name": "my-team",
  "event": "SubagentStop",
  "transcript_path": "optional/path/to/transcript"
}
```

## Installation

### Step 1: Verify Hooks are Executable

```bash
chmod +x .claude/hooks/*.py
```

### Step 2: Install Hooks in Claude Code Settings

Add to your project's `.claude/settings.json`:

```json
{
  "hooks": "./.claude/hooks/hooks.json"
}
```

Or add to user settings `~/.claude/settings.json` for global availability:

```json
{
  "hooks": [
    {
      "event": "SubagentStart",
      "hook": "command",
      "command": "python3 /path/to/meeting-management/.claude/hooks/team-create-add-recorder.py"
    },
    {
      "event": "Notification",
      "hook": "command",
      "command": "python3 /path/to/meeting-management/.claude/hooks/record-message.py"
    },
    {
      "event": "SubagentStop",
      "hook": "command",
      "command": "python3 /path/to/meeting-management/.claude/hooks/generate-meeting-summary.py"
    }
  ]
}
```

### Step 3: Create meeting-recorder Agent

Create a `.claude/agents/meeting-recorder.md` file:

```markdown
---
name: meeting-recorder
description: Records and summarizes team meetings
tools: Read, Write, Grep
model: sonnet
---

# Meeting Recorder

## Purpose
Automatically record team meetings and generate summaries.

## Responsibilities
- Monitor team communications
- Ensure message recording is functioning
- Generate meeting summaries on shutdown
- Identify action items and decisions

## Workflow
1. Receive team creation notification
2. Monitor message events
3. Record all communications
4. Generate summary on shutdown
```

## Usage

### Creating a Team with Meeting Recording

```bash
# Create a new team
/agents
> Create New Team
> Team name: design-review
> Add agents: designer, reviewer

# meeting-recorder will be automatically added
```

### During Team Session

All messages are automatically recorded to `meeting-records/{team_name}/{date}.md`

### After Team Session

Meeting summary is automatically generated at `meeting-records/{team_name}/{date}-summary.md`

## Meeting Records Structure

```
meeting-records/
├── design-review/
│   ├── 2025-01-09.md           # Full transcript
│   └── 2025-01-09-summary.md   # Generated summary
├── backend-planning/
│   ├── 2025-01-09.md
│   └── 2025-01-09-summary.md
└── ...
```

## Transcript Format

### Full Transcript (`2025-01-09.md`)

```markdown
# Meeting Transcript: design-review

**Date:** 2025-01-09
**Started:** 2025-01-09 10:00:00

---

### [10:00:15] designer → team

I've completed the initial mockups for the new dashboard.

### [10:00:30] reviewer → designer

Great work! Can you explain the color scheme choices?

...
```

### Summary (`2025-01-09-summary.md`)

```markdown
# Meeting Summary: design-review

**Date:** 2025-01-09
**Participants:** 3 (designer, reviewer, meeting-recorder)
**Messages:** 24
**Action Items:** 3

## Discussion Summary

### Opening
Meeting initiated by designer

### Discussion
designer: Presented initial mockups for dashboard...
reviewer: Requested clarification on color scheme...

### Closing
Meeting concluded by reviewer

## Action Items

### 1. Update color palette based on accessibility guidelines...

- **Assignee:** designer
- **Source:** reviewer
- **Time:** 10:05:00

...

## Next Steps

1. Review and prioritize action items
2. Assign deadlines to 3 action items
3. Schedule follow-up meeting if needed
4. Update project tracking system
```

## Error Handling

All hooks include comprehensive error handling:

- **Invalid JSON:** Graceful error messages with exit code 1
- **Missing directories:** Automatic creation
- **File locking:** Handles concurrent access
- **Missing transcripts:** Warnings but no failures
- **Malformed timestamps:** Fallback to current time

## Troubleshooting

### Hooks Not Executing

1. Verify Python 3 is installed: `python3 --version`
2. Check hooks are executable: `ls -la .claude/hooks/*.py`
3. Verify hooks.json is valid: `python3 -m json.tool .claude/hooks/hooks.json`
4. Check Claude Code settings: `cat ~/.claude/settings.json`

### Transcripts Not Created

1. Check team_name is being passed correctly
2. Verify write permissions for meeting-records directory
3. Check hook execution logs in Claude Code output

### Action Items Not Identified

1. Ensure messages contain action keywords (action item, to do, task, assign, etc.)
2. Check transcript formatting is correct
3. Verify message content is not empty

## Requirements

- Python 3.6 or higher
- Claude Code with hooks support
- File system write permissions
- fcntl module (for file locking, Unix systems)

## License

MIT

## Contributing

Contributions welcome! Please ensure:
- Comprehensive error handling
- Markdown formatting consistency
- Backward compatibility
- Clear documentation updates
