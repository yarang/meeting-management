---
name: meeting-record
description: >
  Meeting recording commands for Agent Teams. Automatically records all team communications
  when meeting starts and generates structured summaries with action items when meeting ends.

triggers:
  keywords: [meeting, record, transcript, summary, action item, 회의, 기록, 요약,議事, 記録, 要約]

progressive_disclosure:
  enabled: true
  level1_tokens: 150
  level2_tokens: 1200
---

# Meeting Record Skill

Commands for recording and managing Agent Team meetings with automatic transcripts and action item extraction.

## Quick Start

```bash
/meeting-start     # Start recording current meeting
/meeting-end       # End recording and generate summary
/meeting-list      # List all meeting records
/meeting-status    # Show current recording status
```

## Commands

### `/meeting-start`

Start recording the current meeting.

**What it does:**
- Spawns meeting-recorder agent in the current conversation
- Agent monitors all SendMessage communications
- Creates transcript file in `.claude/docs/meeting-records/`

**Example:**
```
User: /meeting-start

Agent: I've spawned a meeting-recorder agent to monitor this conversation.
      All messages will be recorded to the meeting transcript.
```

### `/meeting-end`

End the current meeting and generate summary.

**What it does:**
- Stops message recording
- Generates meeting summary with action items
- Creates summary file alongside transcript

**Example:**
```
User: /meeting-end

Agent: Meeting recording stopped.

      Summary:
      - Duration: 45 minutes
      - Participants: 3
      - Messages: 28
      - Action Items: 5

      Saved to: .claude/docs/meeting-records/2026-03-15-001-api-design-summary.md
```

### `/meeting-list`

List all meeting records.

**What it does:**
- Lists all transcripts and summaries
- Shows meeting ID, date, topic, participant count

### `/meeting-status`

Show current recording status.

**What it does:**
- Shows if recording is active
- Displays current meeting ID if recording

## Output Format

### Transcript Format

Files are saved to `.claude/docs/meeting-records/` with naming:
- `YYYY-MM-DD-NNN-topic.md` (transcript)
- `YYYY-MM-DD-NNN-topic-summary.md` (summary)

**Example transcript:**
```markdown
# Meeting Transcript

**Meeting ID:** 2026-03-15-001
**Team:** my-project
**Topic:** api-design
**Date:** 2026-03-15
**Started:** 2026-03-15 10:00:00

---

### [10:00:15] agent1 → team-lead

Let's start discussing the API design...

### [10:01:30] agent2 → team-lead

I think we should use RESTful architecture...
```

### Summary Format

```markdown
# Meeting Summary

**Meeting ID:** 2026-03-15-001
**Team:** my-project
**Topic:** api-design
**Date:** 2026-03-15
**Participants:** 3 (agent1, agent2, team-lead)
**Messages:** 28
**Action Items:** 5

## Action Items

1. [agent1] Design API endpoints
2. [agent2] Create database schema

## Next Steps

1. Review and prioritize action items
2. Assign deadlines to action items
3. Schedule follow-up meeting if needed
```

## Topic Auto-Detection

Topics are automatically detected from conversation keywords:

| Topic | Keywords |
|-------|----------|
| api-design | api, endpoint, rest, graphql |
| database | database, schema, migration, query |
| auth | auth, login, permission, security |
| frontend | ui, frontend, component, react |
| backend | backend, server, service |
| testing | test, testing, coverage, pytest |
| deployment | deploy, release, ci/cd, docker |
| planning | plan, sprint, backlog, estimate |
| bug | bug, fix, issue, error |
| review | review, pr, code review |
| general | (default) |

## Technical Details

### How Recording Works

1. **Agent Spawning**: `/meeting-start` spawns a background meeting-recorder agent
2. **Message Interception**: Agent receives all SendMessage events via context
3. **Transcript Logging**: Messages are written to transcript file with timestamps
4. **Summary Generation**: `/meeting-end` triggers analysis and summary generation

### File Locations

- **Transcripts**: `.claude/docs/meeting-records/YYYY-MM-DD-NNN-topic.md`
- **Summaries**: `.claude/docs/meeting-records/YYYY-MM-DD-NNN-topic-summary.md`
- **Sequence Tracker**: `.claude/docs/meeting-records/.sequence`

## Usage Workflow

```bash
# Start meeting
/meeting-start

# ... have your discussion ...

# End meeting
/meeting-end

# View records
/meeting-list
```

## Requirements

- Claude Code with Agent Teams support
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` enabled
- Write permissions for `.claude/docs/meeting-records/`
