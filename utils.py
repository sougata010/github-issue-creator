from simple_chalk import green,red

class SaveToken:
    def __init__(self):
        self.BASE_FILE_LOC_GITHUB_CRED = "./creds/github_token.txt"
        self.BASE_FILE_LOC_AI_CRED = "./creds/ai_token.txt"
    def save_github_token(self,token:str):
        try:
            with open(self.BASE_FILE_LOC_GITHUB_CRED,"a") as file:
                file.write(token.strip()+"\n")
            print(green("✔ GitHub Personal Access Token saved to ./creds/github_token.txt"))
        except Exception as e:
            print(red(str(e)))
    def retrive_github_token(self):
        try:
            filemanage = FileManager()
            tokens = filemanage.get_lines(self.BASE_FILE_LOC_GITHUB_CRED)
            return tokens
        except Exception as e:
            print(red(str(e)))
            return []
    def save_ai_token(self,token:str):
            try:
                with open(self.BASE_FILE_LOC_AI_CRED,"a") as file:
                    file.write(token.strip()+"\n")
                print(green("✔ Google Gemini API Key saved to ./creds/ai_token.txt"))
            except Exception as e:
                print(red(str(e)))
    def retrive_ai_token(self):
            try:
                filemanage = FileManager()
                tokens = filemanage.get_lines(self.BASE_FILE_LOC_AI_CRED)
                return tokens[0] if tokens else ""
            except Exception as e:
                print(red(str(e)))
                return ""

class FileManager:
    def __init__(self):
        pass
    def count_line(self,filename:str):
        count = 0
        try:
            with open(filename,"r") as file:
                for i in file:
                    if i.strip():
                        count+=1
            file.close()
            return count
        except Exception as e:
            print(red(str(e)))
            return 0
    def get_lines(self,filename:str):
        try:
            with open(filename,"r") as file:
                tokens = []
                for i in file:
                    cleaned = i.replace("\t", " ").strip()
                    if cleaned:
                        tokens.append(cleaned)
            return tokens
        except Exception as e:
            print(red(str(e)))
            return []