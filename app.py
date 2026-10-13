from github_file import GitHubInit
from art import text2art
from simple_chalk import cyanBright, magenta

Art = text2art("GITHUB ISSUE CREATOR", decoration="wave1")
print(cyanBright(Art))
print(magenta("=" * 60))

gitHub = GitHubInit()
gitHub.create_issue()