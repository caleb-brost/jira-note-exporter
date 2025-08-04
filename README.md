````markdown
# jira-note-exporter

A Python tool that extracts Jira task info from Outlook assignment emails and generates Obsidian-friendly Markdown notes. It includes key metadata, links, and uses a customizable template to help keep sprint tasks organized and accessible.

---

## 1. Install Required Libraries

Run this command to install all necessary Python dependencies:

```bash
pip install -r requirements.txt
````

---

## 2. Configure the Project

1. Copy the config template:

```bash
cp config_template.py config.py
```

2. Edit `config.py` to fill in your personal settings:

* `JIRA_FOLDER_NAME` = Name of the Outlook inbox subfolder where Jira assignment emails are moved.
  Example: `"Jira Assigned Tasks"`

* `VAULT_PATH` = Full path to your Obsidian vault directory.
  Example: `C:/Users/YourName/Documents/Obsidian Vault`

* `TEMPLATE_PATH` = Path to your Obsidian markdown template file.
  Usually stored in a `Templates` folder inside your vault (create one if it doesn’t exist).
  Example: `C:/Users/YourName/Documents/Obsidian Vault/Templates/template.md`

* `EMAIL` = Your Outlook email address.
  Example: `"name.last@company.com"`

* `API_TOKEN` = Your Atlassian API token.
  To create or retrieve your token, visit:
  [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

---

## 3. Set Up Outlook Rule to Auto-Move Jira Emails

To ensure Jira assignment emails are automatically organized into the correct folder:

1. Open **Outlook**.

2. Create a sub-folder in your **Inbox** named **Jira Assigned Tasks**.

3. Then go to the **Settings** → **Mail** → **Rules**.

4. Click **Add New Rule**.

5. Select **Apply rule on messages I receive**, then click **Next**.

6. Under conditions, select:

   * **From people or public group**
     Click the linked text below and enter: `jira@computronix.atlassian.net`

   * **With specific words in the subject or body**
     Click the linked text and add: `assigned this work item to you`

6. Click **Next**.

7. Choose **move it to the specified folder**.
   Click the linked text and select your Jira folder (e.g., `Jira Assigned Tasks`).

8. Click **Next** to add exceptions if any, or skip.

9. Click **Finish**, then **OK** to save the rule (If you already have tasks that need a Obsidian Note, you can manually run the rule).

---

## 4. Usage

Run the Python script to scan your Jira folder emails and generate Markdown notes in your Obsidian vault:

```bash
python your_script_name.py
```

---

*Auto-generated notes will be created using your specified template and saved in your vault.*

---

Feel free to customize the template and config further to fit your workflow!

```

Just copy and paste this whole block into your README file — it’s ready to go!
```
