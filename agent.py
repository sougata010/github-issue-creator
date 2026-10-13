import os
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from prompts import ISSUE_CREATE_SYSTEM_PROMPT
from simple_chalk import cyan, green, yellow, magenta, bold
from datetime import datetime
from typing import List
from utils import SaveToken
from agent_valid import AgentResponse

class Agent:
    def __init__(self):
        self.token_manage = SaveToken()

    def create_agent(self, type: str):
        self.api_key = self.token_manage.retrive_ai_token()
        if not self.api_key:
            print(yellow("ℹ No saved Google Gemini API Key found."))
            self.api_key = input(yellow("Enter your Google Gemini API Key: ")).strip()
            is_save = input(magenta("Do you want to save this Gemini API key locally for future use? [y/N]: "))
            if is_save.lower() in ("y", "yes"):
                self.token_manage.save_ai_token(self.api_key)
            else:
                print(cyan("API key will be used for this session only."))
        if type == "issue_create":
            self.agent = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                api_key=self.api_key,
            )
            return self.agent.with_structured_output(AgentResponse)

    def issue_create(self, issue: str, labels: List[str], image_path: str = None) -> AgentResponse:
        agent = self.create_agent("issue_create")
        print(yellow("\n⏳ Generating issue with Gemini AI..."))
        prompt_text = f"System: {ISSUE_CREATE_SYSTEM_PROMPT}\nTopic: {issue}\nAvailable labels: {labels}"

        if image_path and os.path.isfile(image_path):
            try:
                with open(image_path, "rb") as img_file:
                    b64_image = base64.b64encode(img_file.read()).decode("utf-8")
                ext = os.path.splitext(image_path)[1].lower()
                mime = "image/png" if ext == ".png" else "image/jpeg" if ext in (".jpg", ".jpeg") else "image/webp"
                message_content = [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64_image}"}}
                ]
                res: AgentResponse = agent.invoke([HumanMessage(content=message_content)])
            except Exception:
                res: AgentResponse = agent.invoke(prompt_text)
        else:
            res: AgentResponse = agent.invoke(prompt_text)
        print(green("\n✨ Issue Generated Successfully:"))
        print(cyan("  • Title  : ") + bold(res.title))
        print(magenta("  • Type   : ") + res.type)
        print(yellow("  • Labels : ") + (", ".join(res.label) if res.label else "None"))
        print(cyan("─" * 60))
        os.makedirs("./out", exist_ok=True)
        safe_name = "".join(c if c.isalnum() else "_" for c in res.title[:30]).strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"./out/issue_{safe_name}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(f"Title: {res.title}\nType: {res.type}\nLabels: {res.label}\n\n{res.body}")
        print(green(f"💾 Saved draft to: {filename}\n"))
        return res
    
