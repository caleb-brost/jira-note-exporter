import requests
from requests.auth import HTTPBasicAuth
import json
from config import JIRA_URL, MAX_RESULTS, EMAIL, ASSIGNEE, API_TOKEN
from logger import debug_all
from pprint import pprint
from jira_extract import extract_all
import os

def write_json_template(issue_json, template_path, vault_path):
    """
    Write a Jira issue to a Markdown file using a template.

    Args:
        issue_json (dict): The extracted issue info.
        template_path (str): Full path to your template file.
        vault_path (str): Path to your Obsidian vault.
    """
    # Read the template
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Replace placeholders with JSON values
    md_content = template
    for key, value in issue_json.items():
        placeholder = f"{{{{{key}}}}}"  # e.g., {{summary}}
        md_content = md_content.replace(placeholder, str(value or ""))

    # Determine output file path
    filename = f"{issue_json.get('key', 'UNKNOWN')}.md"
    filepath = os.path.join(vault_path, filename)

    # Write the filled template
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Note written to {filepath}")

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
            debug_all(issue)
            write_json_template(
                extract_all(issue), 
                "C:\\Users\\Caleb.Brost\\OneDrive - Computronix\\Documents\\Obsidian Vault\\Templates\\template.md", 
                "C:\\Users\\Caleb.Brost\\OneDrive - Computronix\\Documents\\Obsidian Vault\\Temp"
            )
            
    else:
        print(f"Error {response.status_code}: {response.text}")


if __name__ == "__main__":
    main()
