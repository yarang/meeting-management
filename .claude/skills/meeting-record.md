---
name: meeting-record
description: Manages meeting records with slash commands for creating, viewing, searching, summarizing, and extracting action items from meetings. Provides structured storage with YAML frontmatter and search capabilities.
---

# Meeting Record Management Skill

## Quick Start

Install this skill by creating the meeting-record.md file in your .claude/skills directory.

**Key Commands:**
- `/meeting-start` - Start recording a new meeting
- `/meeting-end` - End current meeting and generate report
- `/meeting-list` - List all meeting records
- `/meeting-search <query>` - Search meeting transcripts
- `/meeting-summary <id>` - Get summary of specific meeting
- `/meeting-actions <id>` - Extract action items from meeting

**Data Storage:** Records stored in `meeting-records/` directory with YAML frontmatter

**Format:** Markdown files with structured metadata and transcript content

## Implementation Guide

### Directory Structure

Meeting records are stored in the `meeting-records/` directory with the following structure:

```
meeting-records/
├── 2026-03-14-team-meeting-001.md
├── 2026-03-14-planning-session-002.md
└── 2026-03-15-code-review-003.md
```

Each meeting file contains YAML frontmatter with metadata and markdown content for the meeting transcript.

### Meeting File Format

Meeting files use YAML frontmatter followed by markdown content:

```yaml
---
title: "Team Meeting"
date: "2026-03-14T14:30:00"
duration: 45
participants: ["john@company.com", "sarah@company.com", "mike@company.com"]
facilitator: "john@company.com"
location: "Conference Room A"
agenda: ["Project Status", "Sprint Planning", "Roadmap Discussion"]
status: "completed"
recording_started: "2026-03-14T14:30:00"
recording_ended: "2026-03-14T15:15:00"
---

# Meeting Transcript

## Attendees Present
- John (Facilitator)
- Sarah
- Mike

## Agenda Items

### 1. Project Status
- John presented the current project status with 85% completion rate
- Sarah asked about resource allocation for final phase
- Mike provided updates on integration testing results

### 2. Sprint Planning
- Reviewed upcoming sprint goals and deliverables
- Discussed team capacity and task assignments
- Identified potential blockers and mitigation strategies

### 3. Roadmap Discussion
- Reviewed Q2 product roadmap and milestones
- Discussed potential feature additions and prioritization
- Agreed on timeline adjustments based on current progress

## Action Items
- John to finalize resource allocation by Friday
- Sarah to schedule integration testing session
- Mike to prepare technical documentation for new features
```

### Slash Command Implementations

#### `/meeting-start` - Start Recording a New Meeting

Triggers a meeting initialization workflow:

1. Prompt for meeting details (title, date, time, participants, agenda)
2. Create meeting record file with initial metadata
3. Set meeting status to "active"
4. Provide meeting ID and instructions for recording

**Implementation:**
```javascript
const meetingRecordManager = new MeetingRecordManager();
const meeting = await meetingRecordManager.startMeeting({
  title: "Team Meeting",
  date: new Date(),
  participants: ["john@company.com"],
  facilitator: "john@company.com",
  agenda: ["Project Status", "Sprint Planning"]
});
```

#### `/meeting-end` - End Current Meeting and Generate Report

Triggers meeting completion workflow:

1. Set meeting status to "completed"
2. Calculate meeting duration
3. Generate automated summary using AI
4. Extract action items from transcript
5. Save final meeting record

**Implementation:**
```javascript
const summary = await meetingRecordManager.endMeeting(meetingId);
const actionItems = await meetingRecordManager.extractActionItems(meetingId);
```

#### `/meeting-list` - List All Meeting Records

Retrieves and displays all meeting records:

1. Scan `meeting-records/` directory
2. Parse YAML frontmatter from each file
3. Display meeting list with key metadata
4. Support filtering by date range, participants, or status

**Implementation:**
```javascript
const meetings = await meetingRecordManager.listMeetings({
  startDate: "2026-03-01",
  endDate: "2026-03-31",
  participant: "john@company.com",
  status: "completed"
});
```

#### `/meeting-search <query>` - Search Meeting Transcripts

Performs full-text search across meeting content:

1. Parse all meeting files and extract content
2. Perform keyword search in title, agenda, and transcript
3. Return matching meetings with relevance scores
4. Support search by date, participants, or content

**Implementation:**
```javascript
const results = await meetingRecordManager.searchMeetings({
  query: "resource allocation",
  participants: ["john@company.com"],
  dateRange: { start: "2026-03-01", end: "2026-03-31" }
});
```

#### `/meeting-summary <id>` - Get Summary of Specific Meeting

Generates comprehensive meeting summary:

1. Load meeting record by ID
2. Extract key discussion points and decisions
3. Generate structured summary with AI assistance
4. Provide overview of meeting outcomes

**Implementation:**
```javascript
const meeting = await meetingRecordManager.getMeeting(meetingId);
const summary = await meetingRecordManager.generateSummary(meeting);
```

#### `/meeting-actions <id>` - Extract Action Items from Meeting

Automates action item extraction:

1. Parse meeting transcript and discussion content
2. Identify action item patterns and assignments
3. Extract owner, task description, and due dates
4. Return structured action items list

**Implementation:**
```javascript
const actionItems = await meetingRecordManager.extractActionItems(meetingId);
```

### Search Capabilities

The skill supports multiple search strategies:

**By Date:** Search meetings within specific date ranges
**By Participants:** Find meetings involving specific team members
**By Topics:** Search meeting content for specific keywords or topics
**By Status:** Filter by meeting status (active, completed, cancelled)

### Data Management

**File Organization:** Meeting files are organized chronologically with unique IDs
**Metadata:** Comprehensive metadata including timestamps, participants, and meeting details
**Storage:** Efficient storage with YAML frontmatter for structured data access
**Backup:** Automatic backup of meeting records before major operations

### Integration Patterns

**Integration with Calendar:** Link meetings to calendar events for scheduling
**Integration with Project Management:** Sync action items with task tracking systems
**Integration with Communication:** Share meeting summaries and action items via email or chat
**Integration with Documentation:** Archive meeting records in project documentation

---

## Advanced Features

### Automated Summary Generation

The skill uses AI to generate structured meeting summaries including:

- Key discussion points and decisions
- Action items and responsible parties
- Meeting outcomes and next steps
- Decisions made and rationale

### Action Item Extraction

Automatically identifies and extracts action items from meeting content:

- Extracts task descriptions and owners
- Identifies due dates and priorities
- Categorizes action items by type
- Tracks completion status

### Meeting Analytics

Provides analytics on meeting patterns:

- Meeting frequency and duration trends
- Participant attendance and engagement
- Action item completion rates
- Discussion topic analysis

---

## Works Well With

**Skills:**
- moai-docs-generation - Generate meeting documentation and reports
- moai-formats-data - Optimize meeting data storage and retrieval
- moai-library-mermaid - Create meeting process flow diagrams

**Commands:**
- /moai:3-sync - Synchronize meeting records with project documentation
- /moai:9-feedback - Generate feedback reports from meeting outcomes

**Integration:**
- Calendar systems for meeting scheduling
- Project management tools for action item tracking
- Communication platforms for meeting notifications

---

## File Paths

**Meeting Records:** `meeting-records/`
**Configuration:** `.claude/skills/meeting-record.md`
**Data Storage:** Individual markdown files with YAML frontmatter

---

## Technical Specifications

**Supported File Formats:** Markdown with YAML frontmatter
**Search Algorithm:** Full-text search with relevance scoring
**Data Compression:** Efficient storage with structured metadata
**Backup Strategy:** Automatic backup before major operations
**Performance:** Optimized for large volumes of meeting records

---

Status: Production Ready
Last Updated: 2026-03-14
Version: 1.0.0
Maintained by: Meeting Management Team
Generated with: MoAI-ADK Skill Factory