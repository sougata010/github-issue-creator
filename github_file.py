from github import Github,Auth
import os
from datetime import datetime
from simple_chalk import red,yellow,magenta,cyan,magentaBright,green,blue
from utils import SaveToken,FileManager
import questionary
from agent import Agent

class GitHubInit:
    def __init__(self):
        self.agent = Agent()
        self.saved_token = SaveToken()
        tokens = self.saved_token.retrive_github_token()
        if len(tokens)<=0:
            print(yellow("ℹ No saved GitHub Personal Access Token found."))
            self.token = input(yellow("Enter your GitHub Personal Access Token: ")).strip()
            is_save = input(magenta("Do you want to save this GitHub token locally for future use? [y/N]: "))
            if is_save.lower() in ("y", "yes"):
                self.saved_token.save_github_token(self.token)
            else:
                print(cyan("Token will be used for this session only."))
        else:
            choices = tokens + ["➕ Enter a new GitHub Token"]
            selected = questionary.select("Choose which saved GitHub token to use: ", choices).ask()
            if selected=="➕ Enter a new GitHub Token" or selected is None:
                self.token = input(yellow("Enter your GitHub Personal Access Token: ")).strip()
                is_save = input(magenta("Do you want to save this GitHub token locally for future use? [y/N]: "))
                if is_save.lower() in ("y", "yes"):
                    self.saved_token.save_github_token(self.token)
                else:
                    print(cyan("Token will be used for this session only."))
            else:
                self.token = selected
        self.auth = Auth.Token(self.token)
        self.g = Github(auth=self.auth)
    def view_repo(self):
        repos = []
        try:
            for repo in self.g.get_user().get_repos():
                repos.append(repo.name)
            if len(repos)<=0:
                print(red("No repositories found in this GitHub account."))
                return ""
            selected = questionary.select("Select the repository to create an issue in: ", repos).ask()
            return selected
        except Exception as e:
            print(red(f"Error fetching repositories: {str(e)}"))

    def select_issue(self):
        path = "./issues"
        os.makedirs(path, exist_ok=True)
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        if not files:
            print(yellow("ℹ No issue files found in ./issues folder."))
            return input(yellow("Enter your issue description manually: ")).strip()
        selected = questionary.select("Select the issue file to load: ", files).ask()
        if not selected:
            return None
        file_path = os.path.join(path, selected)
        filemanager = FileManager()
        if filemanager.count_line(file_path)<=0:
            i = input(yellow("No issues found in this file. Want to type your issue manually? [y/N]: "))
            if (i.lower()=="n" or i.lower()=="no"):
                return None
            issue = input(yellow("Enter your issue description: "))
            return issue
        else:
            issues = filemanager.get_lines(file_path)
            selected = questionary.select("Select which issue you want to process: ", issues).ask()
            return selected
    def create_issue(self):
        self.repo_name = self.view_repo()
        self.issue = self.select_issue()
        if self.issue is None:
            return None

        # Image attachment prompt
        image_path = None
        attach_img = input(magenta("\nDo you want to attach an image/screenshot from your PC? [y/N]: ")).strip()
        if attach_img.lower() in ("y", "yes"):
            raw_path = input(yellow("Enter the local image path (e.g. C:/path/to/screenshot.png): ")).strip()
            clean_path = raw_path.strip('"').strip("'")
            if os.path.isfile(clean_path):
                image_path = clean_path
                print(green(f"✔ Image attached: {clean_path}"))
            else:
                print(red(f"❌ File not found at '{clean_path}'. Proceeding without image."))

        try:
            for repo in self.g.get_user().get_repos():
                if self.repo_name == repo.name:
                    repo_sl = repo
            available_labels = {label.name: label for label in repo_sl.get_labels()}
            issue_res = self.agent.issue_create(issue=self.issue, labels=available_labels, image_path=image_path)

            # Upload image to repo if provided
            image_url = None
            if image_path and os.path.isfile(image_path):
                try:
                    print(yellow("📤 Uploading image attachment to repository..."))
                    with open(image_path, "rb") as f:
                        img_bytes = f.read()
                    ext = os.path.splitext(image_path)[1].lower() or ".png"
                    img_name = f"issue_img_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                    upload_res = repo_sl.create_file(
                        path=f"assets/issue_attachments/{img_name}",
                        message=f"Attach image for issue: {img_name}",
                        content=img_bytes
                    )
                    image_url = upload_res["content"].download_url
                    print(green("✔ Image uploaded successfully to GitHub!"))
                except Exception as up_err:
                    print(red(f"Warning: Could not upload image to repo ({str(up_err)}). Continuing without attachment."))

            issue_body = issue_res.body
            if image_url:
                issue_body += f"\n\n### Attachments\n![Screenshot]({image_url})\n"

            select_assignes = [u.login for u in repo_sl.get_collaborators()]
            selected = questionary.select("Choose assignee for this issue: ", select_assignes + ["None"]).ask()
            assignee = None if selected in ("None", None) else selected

            issue_created = repo_sl.create_issue(
                title=issue_res.title,
                body=issue_body,
                assignee=assignee,
                labels=issue_res.label
            )

            print(green("\n🚀 Issue Created Successfully on GitHub!"))
            print(cyan("🔗 Issue URL: ") + blue(issue_created.html_url))
            print(green("─" * 60))
        except Exception as e:
            print(red(str(e)))
            