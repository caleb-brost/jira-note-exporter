from jira_utils import format_jira_time, jira_seconds_to_hours

def extract_basic_info(issue):
    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    PPI_link = summary.split()[0] if summary.startswith("PPI") else None
    print(PPI_link)

    return {
        "key": issue.get("key") or "None",
        "summary": fields.get("summary") or "None",
        "ppi:": PPI_link or "None",
    }

def extract_description(issue, indent=0):
    """
    Recursively convert Atlassian-style description JSON into a Markdown string
    and return it as a dictionary with key 'description'.

    Args:
        issue (dict): Jira issue dictionary.
        indent (int): Current indentation for nested content.

    Returns:
        dict: {'description': Markdown-formatted string}
    """
    description_node = issue.get("fields", {}).get("description")
    if not description_node:
        return {"description": "No description.\n"}

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
                output += "  \n"
            elif node_type == "paragraph":
                if "content" in node:
                    output += _parse_node(node["content"], indent)
                output += "\n\n"
            elif node_type == "blockquote":
                if "content" in node:
                    content_md = _parse_node(node["content"], indent)
                    for line in content_md.splitlines():
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

    output = _parse_node(description_node, indent)
    return {"description": output}

def extract_state_info(issue):
    fields = issue.get("fields", {})
    return {
        "status": fields.get("status", {}).get("name") or "None",
        "priority": fields.get("priority", {}).get("name") or "None",
        "created": format_jira_time(fields.get("created")) or "None",
        "updated": format_jira_time(fields.get("updated")) or "None",
        "duedate": format_jira_time(fields.get("duedate")) or "None",
    }

def extract_users(issue):
    fields = issue.get("fields", {})
    
    dict = {}
    for key in ["assignee", "reporter", "creator"]:
        user = fields.get(key)
        if user:
            dict[key] = f"{user.get('displayName')} ({user.get('emailAddress')})"
        else:
            dict[key] = f"{key.capitalize()}: ''"

    return dict

def extract_labels(issue):
    labels = issue.get("fields", {}).get("labels", [])
    return {"labels": ", ".join(labels)} if labels else {"labels": ""}
 
def extract_project_info(issue):
    project = issue.get("fields", {}).get("project", {})
    return {"project": project.get("name") or "None"}

def extract_time_info(issue):
    fields = issue.get("fields", {})
    print(jira_seconds_to_hours(fields.get("timeoriginalestimate")))
    return {
        "timeoriginalestimate": jira_seconds_to_hours(fields.get("timeoriginalestimate")) or "None",
        "timeestimate": jira_seconds_to_hours(fields.get("timeestimate")) or "None",
        "timespent": jira_seconds_to_hours(fields.get("timespent")) or "None",
    }

def extract_fix_versions(issue):
    versions = issue.get("fields", {}).get("fixVersions", [])
    str = ""
    for version in versions:
        str += f"{version.get('name')}\n"
    return {"fixversion": str or "None"}

def extract_customfields(issue):
    fields = issue.get("fields", {})
    str = ""
    for key, value in fields.items():
        if key.startswith("customfield_") and value not in [None, [], ""]:
            if isinstance(value, dict):
                display = value.get("value") or value.get("name")
                if display:
                    str += display
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict):
                    display = value[0].get("value") or value[0].get("name")
                    if display:
                        str += display
    return {"customfields": str or "None"}

def extract_all(issue):
    result = {}

    result.update(extract_basic_info(issue))
    result.update(extract_description(issue, 0))
    result.update(extract_state_info(issue))
    result.update(extract_users(issue))
    result.update(extract_labels(issue))
    result.update(extract_project_info(issue))
    result.update(extract_time_info(issue))
    result.update(extract_fix_versions(issue))
    result.update(extract_customfields(issue))

    return result