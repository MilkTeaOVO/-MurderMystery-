import os
class EnvSetting():
    def __init__(self):
        self.API_KEY = "YOUR_API_KEY"
        self.BASE_URL = "YOUR_URL"
        self.name = __class__.__name__
        Home_dir = os.path.expanduser("~")
        self.env_dir = os.path.join(Home_dir,".API_ENV")
        if self.check_file():
            print("[SUCCESS] Your Environment have already set!")
            print(f"You can use use {self.name}.API_KEY & {self.name}.BASE_URL to get it")
            self.Read_env()
        else:
            print("[ERROR] Your API-Environment havent set!!!")
            print(f"If you need to use API, please use {self.name}.set_API(API,BASE_URL) or {self.name}.input_API to set")

    def check_file(self):
        if os.path.exists(self.env_dir):
            return True
        else:
            return False

    def Update_set(self):
        with open(self.env_dir,"w") as env:
            env.write(self.API_KEY+"\n"+self.BASE_URL)
    def Input_set(self):
        self.API_KEY = input("Please write your API_KEY:")
        self.BASE_URL = input("Please write your BASE_URL:")
        self.Update_set()
    def Read_env(self):
        with open(self.env_dir,"r") as env:
            envlist = env.read().split("\n")
        self.API_KEY = envlist[0]
        self.BASE_URL = envlist[1]

if __name__ == "__main__":
    my_env = EnvSetting()

    