---
paths: "**/.claude/teams/**"
---

# Meeting Auto-Recorder Rule

## Requirement
All Agent Teams MUST include meeting-recorder agent.

## Enforcement
### Hook Specification
Trigger: TeamCreate operations
Action: Automatically add meeting-recorder agent to the team
Integration: Ensure meeting-recorder can record all communications

### Configuration Requirements
The meeting-recorder agent must be added with the following configuration:
- **name**: "meeting-recorder"
- **mode**: "acceptEdits" (can write meeting records)
- **auto-start**: True (start recording when team is created)

### Implementation Guidance
When a TeamCreate operation is detected:
1. Validate that meeting-recorder agent exists in the agent registry
2. Add meeting-recorder to the team roster with the specified configuration
3. Configure recording capabilities for all team communications
4. Ensure meeting-recorder has permission to access team conversation history
5. Initialize recording system for the new team

### Recording Capabilities
The meeting-recorder agent should provide:
- Full conversation transcript capture
- Action item tracking and categorization
- Decision recording with context
- Timeline-based meeting segmentation
- Export capabilities for meeting summaries
- Real-time recording status monitoring

### Integration with TeamCreate Workflow
The hook should integrate seamlessly with the existing TeamCreate process:
- Intercept team creation requests before finalization
- Verify meeting-recorder availability and permissions
- Add recording configuration to team metadata
- Provide confirmation to team lead of recording initiation
- Maintain team recording configuration in team manifest

### Quality Assurance
Recording must meet the following standards:
- 100% conversation coverage with no gaps
- Accurate timestamping and speaker attribution
- Secure storage with appropriate access controls
- Configurable retention policies
- Backup and disaster recovery procedures
- Compliance with organizational recording policies

### Error Handling
The hook should handle potential failures:
- Fallback mechanism if meeting-recorder unavailable
- Alert system for recording failures
- Graceful degradation without blocking team creation
- Recovery procedures for interrupted recordings
- Audit trail for all recording operations