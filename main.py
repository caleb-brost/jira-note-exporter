import win32com.client
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from dateutil import parser
from datetime import datetime

# ========== CONFIG ==========

from jira_config import JIRA_FOLDER_NAME, VAULT_PATH, TEMPLATE_PATH, EMAIL, API_TOKEN, SAVE_JSON

# ============================

def connect_to_email():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6 = inbox
    for folder in inbox.Folders:
        if folder.Name == JIRA_FOLDER_NAME:
            return folder.Items
    raise Exception(f"Folder '{JIRA_FOLDER_NAME}' not found.")

def fetch_new_jira_emails():
    items = connect_to_email()
    items.Sort("[ReceivedTime]", True)  # sort newest first
    return [item for item in items if "jira" in item.Subject.lower()]

def generate_markdown(task_info):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    for key, val in task_info.items():
        template = template.replace(f"{{{{{key}}}}}", str(val))

    return template

def write_markdown_file(filename, content):
    filepath = os.path.join(VAULT_PATH, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✔ Created note: {filepath}")

def parse_jira_email(msg):
    soup = BeautifulSoup(str(msg.HTMLBody), "html.parser")
    match = soup.find("a", string=re.compile(r"[A-Z]+-\d+"))
    if match:
        print("✔ Found Jira task link:", match.text)
    return match

def fetch_jira_issue(issue_key):
    url = f"https://computronix.atlassian.net/rest/api/2/issue/{issue_key}"
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()

    issue_json = response.json()

    if SAVE_JSON:
        with open(f"{issue_key}.json", "w", encoding="utf-8") as f:
            json.dump(issue_json, f, indent=2)
        print(f"✔ Saved JSON data for {issue_key} to {issue_key}.json")

    return issue_json

def extract_task_info(issue_json):
    fields = issue_json.get("fields", {})
    return {
        "key": issue_json.get("key", "N/A"),
        "summary": fields.get("summary", ""),
        "description": fields.get("description", "No description provided."),
        "reporter": fields.get("reporter", {}).get("displayName", "N/A"),
        "assignor": fields.get("customfield_10072", {}).get("displayName", "N/A"),
        "assignee": fields.get("assignee", {}).get("displayName", "Unassigned"),
        "project": fields.get("project", {}).get("name", "N/A"),
        "sprint": fields.get("customfield_10020", [{}])[0].get("name", "N/A") if fields.get("customfield_10020") else "N/A",
        "created": fields.get("created", "N/A"),
        "duedate": fields.get("duedate", "N/A"),
        "estimate": fields.get("timetracking", {}).get("originalEstimate", "N/A"),
        "labels": ", ".join(fields.get("labels", [])) or "None",
        "issuetype": fields.get("issuetype", {}).get("name", "N/A"),
        "priority": fields.get("priority", {}).get("name", "N/A"),
        "createddate": parser.parse(fields["created"]).strftime("%Y-%m-%d %H:%M") if fields.get("created") else "N/A",
        "syncdate": datetime.now().strftime("%Y-%m-%d %H:%M")

    }

def main():
    emails = fetch_new_jira_emails()
    for email in emails:
        task = parse_jira_email(email)
        if not task:
            continue
        task_key = task.text.strip()
        issue_json = fetch_jira_issue(task_key)
        task_info = extract_task_info(issue_json)
        markdown = generate_markdown(task_info)
        write_markdown_file(f"{task_key}.md", markdown)

if __name__ == "__main__":
    main()
