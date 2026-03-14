#!/usr/bin/env python3
"""
Hook: Team Creation - Add Meeting Recorder
Trigger: After TeamCreate
Purpose: Automatically add meeting-recorder agent to new teams
"""

import json
import sys
import os

def main():
    """
    Read team creation event from stdin and add meeting-recorder if not present.

    Expected JSON input:
    {
        "team_name": "team-name",
        "members": ["agent1", "agent2"],
        "event": "TeamCreate"
    }
    """
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())

        team_name = input_data.get("team_name", "")
        members = input_data.get("members", [])

        if not team_name:
            print("Error: team_name is required", file=sys.stderr)
            sys.exit(1)

        # Check if meeting-recorder is already in the team
        recorder_agent = "meeting-recorder"

        if recorder_agent not in members:
            members.append(recorder_agent)

            # Update team configuration
            teams_config_path = os.path.expanduser("~/.claude/teams/{team_name}/config.json")

            try:
                with open(teams_config_path, 'r') as f:
                    team_config = json.load(f)

                team_config["members"] = members

                with open(teams_config_path, 'w') as f:
                    json.dump(team_config, f, indent=2)

                print(f"✓ Added {recorder_agent} to team '{team_name}'")

                # Return updated configuration
                output = {
                    "status": "success",
                    "team_name": team_name,
                    "members": members,
                    "message": f"Added {recorder_agent} to team"
                }
                print(json.dumps(output))

            except FileNotFoundError:
                # Team config file not found, might be newly created team
                # Just return the updated member list
                output = {
                    "status": "success",
                    "team_name": team_name,
                    "members": members,
                    "message": f"Added {recorder_agent} to team (config pending)"
                }
                print(json.dumps(output))
        else:
            output = {
                "status": "success",
                "team_name": team_name,
                "members": members,
                "message": f"{recorder_agent} already in team"
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
