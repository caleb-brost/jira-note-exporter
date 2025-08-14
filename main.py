import requests
from requests.auth import HTTPBasicAuth
import json
from config import JIRA_URL, MAX_RESULTS, EMAIL, ASSIGNEE, API_TOKEN
from jira_utils import format_jira_time, jira_seconds_to_hours
from terminal_styles import style

def print_basic_info(issue):
    fields = issue.get("fields", {})
    print(style("=== Basic Info ===", color="cyan", bold=True))
    print(style(f"Key: {issue.get('key')}", color="white"))
    print(style(f"Summary: {fields.get('summary')}", color="white"))

def parse_description(issue, indent=0):
    """
    Recursively convert Atlassian-style description JSON into a Markdown string.

    Args:
        issue (dict): Jira issue dictionary.
        indent (int): Current indentation for nested content.

    Returns:
        str: Markdown-formatted string.
    """
    description_node = issue.get("fields", {}).get("description")
    if not description_node:
        return "No description.\n"

    def _parse_node(node, indent=0):
        output = ""
        if isinstance(node, list):
            for item in node:
                output += _parse_node(item, indent)
        elif isinstance(node, dict):
            node_type = node.get("type")
            if node_type == "text":
                output += " " * indent + node.get("text", "")
            elif node_type == "hardBreak":
                output += "  \n"  # Markdown line break
            elif node_type == "paragraph":
                if "content" in node:
                    output += _parse_node(node["content"], indent)
                output += "\n\n"
            elif node_type == "blockquote":
                if "content" in node:
                    content_md = _parse_node(node["content"], indent)
                    lines = content_md.splitlines()
                    for line in lines:
                        output += " " * indent + "> " + line + "\n"
                output += "\n"
            elif node_type == "panel":
                panel_type = node.get("attrs", {}).get("panelType", "info").upper()
                if "content" in node:
                    content_md = _parse_node(node["content"], indent)
                    output += f"\n```{panel_type}\n{content_md}```\n\n"
            else:
                if "content" in node:
                    output += _parse_node(node["content"], indent)
        return output

    return _parse_node(description_node, indent)

    """
    Recursively convert Atlassian-style description JSON into Markdown string.
    
    Args:
        description_node (dict or list): The description content or node.
        indent (int): Current indentation for nested content.
    
    Returns:
        str: Markdown-formatted string.
    """
    output = ""

    description_node = issue["fields"]["description"]

    if not description_node:
        print("No description.")
        return
    
    if isinstance(description_node, list):
        for item in description_node:
            output += print_description(item)
    elif isinstance(description_node, dict):
        node_type = description_node.get("type")
        
        if node_type == "text":
            output += " " * indent + description_node.get("text", "")
        elif node_type == "hardBreak":
            output += "  \n"  # Markdown line break
        elif node_type == "paragraph":
            if "content" in description_node:
                output += print_description(description_node["content"], indent)
            output += "\n\n"  # separate paragraphs in Markdown
        elif node_type == "blockquote":
            if "content" in description_node:
                content_md = print_description(description_node["content"], indent)
                # Add > to each line
                lines = content_md.splitlines()
                for line in lines:
                    output += " " * indent + "> " + line + "\n"
            output += "\n"
        elif node_type == "panel":
            panel_type = description_node.get("attrs", {}).get("panelType", "info").upper()
            if "content" in description_node:
                content_md = print_description(description_node["content"], indent)
                # Render panel as a fenced block with panel type
                output += f"\n```{panel_type}\n{content_md}```\n\n"
        else:
            if "content" in description_node:
                output += print_description(description_node["content"], indent)
    
    print(f"Description: {output}")

def print_state_info(issue):
    fields = issue.get("fields", {})
    print(style("=== State Info ===", color="cyan", bold=True))
    print(style(f"Status: {fields.get('status', {}).get('name')}", color="white"))
    print(style(f"Priority: {fields.get('priority', {}).get('name')}", color="white"))
    print(style(f"Created: {format_jira_time(fields.get('created'))}", color="white"))
    print(style(f"Updated: {format_jira_time(fields.get('updated'))}", color="white"))
    print(style(f"Due Date: {fields.get('duedate')}", color="white"))

def print_users(issue):
    fields = issue.get("fields", {})
    print(style("=== Users ===", color="cyan", bold=True))
    for key in ["assignee", "reporter", "creator"]:
        user = fields.get(key)
        if user:
            print(style(f"{key.capitalize()}: {user.get('displayName')} ({user.get('emailAddress')})", color="white"))

def print_labels(issue):
    labels = issue.get("fields", {}).get("labels", [])
    if labels:
        print(style("=== Labels ===", color="cyan", bold=True))
        for label in labels:
            print(style(f"  - {label}", color="magenta"))

def print_project_info(issue):
    project = issue.get("fields", {}).get("project", {})
    if project:
        print(style("=== Project ===", color="cyan", bold=True))
        print(style(f"Project Name: {project.get('name')}", color="white"))

def print_time_info(issue):
    fields = issue.get("fields", {})
    print(style("=== Time Tracking ===", color="cyan", bold=True))
    print(style(f"Original Estimate: {jira_seconds_to_hours(fields.get('timeoriginalestimate'))}", color="white"))
    print(style(f"Remaining Estimate: {jira_seconds_to_hours(fields.get('timeestimate'))}", color="white"))
    print(style(f"Time Spent: {jira_seconds_to_hours(fields.get('timespent'))}", color="white"))

def print_fix_versions(issue):
    versions = issue.get("fields", {}).get("fixVersions", [])
    if versions:
        print(style("=== Fix Versions ===", color="cyan", bold=True))
        for v in versions:
            print(style(f"  - {v.get('name')}", color="green"))

def print_customfields(issue):
    fields = issue.get("fields", {})
    print(style("=== Non-empty Custom Fields ===", color="cyan", bold=True))
    for key, value in fields.items():
        if key.startswith("customfield_") and value not in [None, [], ""]:
            if isinstance(value, dict):
                display = value.get("value") or value.get("name")
                if display:
                    print(style(display, color="magenta"))
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    display = value[0].get("value") or value[0].get("name")
                    if display:
                        print(style(display, color="magenta"))

def print_all(issue):
    print(style("===================== Issue =====================", color="blue", bold=True))
    print_basic_info(issue)
    print(style("=== Description ===", color="cyan", bold=True))
    print(parse_description(issue))
    print_state_info(issue)
    print_users(issue)
    print_labels(issue)
    print_project_info(issue)
    print_time_info(issue)
    print_fix_versions(issue)
    print_customfields(issue)

def main():
    # JQL query: assigned to a specific user
    jql = f'assignee = "{ASSIGNEE}" ORDER BY created DESC'

    url = f"{JIRA_URL}/rest/api/3/search"
    params = {"jql": jql, "maxResults": MAX_RESULTS}

    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, params=params, auth=auth)

    if response.status_code == 200:
        data = response.json()
        issues = data.get("issues", [])
        for issue in issues:
            print_all(issue)
        
    else:
        print(f"Error {response.status_code}: {response.text}")


if __name__ == "__main__":
    main()
