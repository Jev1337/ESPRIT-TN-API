import requests
from termcolor import colored
from bs4 import BeautifulSoup


class esprit:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        
    def login(self):
        print(colored("[+] Starting the script", "green"))
        print(colored("[+] Init Session", "green"))
        print(colored("[+] Sending the first request", "green"))
        url = "https://esprit-tn.com/esponline/Online/default.aspx"
        response = self.session.get(url)
        
        # Find input with name __VIEWSTATE, __VIEWSTATEGENERATOR, __EVENTVALIDATION
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
            viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
            eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
        except TypeError:
            with open("login_failed.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            raise Exception("[-] Couldn't find the required fields, page content saved in login_failed.html")
        
        # Check if we need to handle the "I'm not a robot" checkbox
        checkbox = soup.find("input", {"name": "ctl00$ContentPlaceHolder1$chkImage"})
        if checkbox:
            print(colored("[+] Found 'I'm not a robot' checkbox, checking it first", "green"))
            # First, check the checkbox without any login credentials
            data = {
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$chkImage",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": viewstate,
                "__VIEWSTATEGENERATOR": viewstategenerator,
                "__EVENTVALIDATION": eventvalidation,
                "ctl00$ContentPlaceHolder1$TextBox1": "",
                "ctl00$ContentPlaceHolder1$TextBox5": "",
                "ctl00$ContentPlaceHolder1$TextBox6": "",
                "ctl00$ContentPlaceHolder1$TextBox3": "",
                "ctl00$ContentPlaceHolder1$TextBox4": "",
                "ctl00$ContentPlaceHolder1$pass_parent": "",
                "ctl00$ContentPlaceHolder1$chkImage": "on"  # Explicitly check the checkbox
            }
            response = self.session.post(url, data=data)
            soup = BeautifulSoup(response.text, "html.parser")
            try:
                viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
                viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
                eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
            except TypeError:
                with open("login_failed.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                raise Exception("[-] Couldn't find the required fields after checkbox, page content saved in login_failed.html")
        
        # Phase 1: Send username
        print(colored("[+] Sending the login request (Phase 1)", "green"))
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__EVENTVALIDATION": eventvalidation,
            "ctl00$ContentPlaceHolder1$TextBox1": "",
            "ctl00$ContentPlaceHolder1$TextBox5": "",
            "ctl00$ContentPlaceHolder1$TextBox6": "",
            "ctl00$ContentPlaceHolder1$TextBox3": self.username,
            "ctl00$ContentPlaceHolder1$Button3": "Suivant",
            "ctl00$ContentPlaceHolder1$TextBox4": self.username,
            "ctl00$ContentPlaceHolder1$pass_parent": self.password,
        }
        response = self.session.post(url, data=data)
        
        # Phase 2: Handle password form
        print(colored("[+] Sending the login request (Phase 2)", "green"))
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
            viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
            eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
        except TypeError:
            with open("login_failed.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            raise Exception("[-] Couldn't find the required fields (Phase 2), page content saved in login_failed.html")
        
        data = {
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            "__EVENTVALIDATION": eventvalidation,
            "ctl00$ContentPlaceHolder1$TextBox1": "",
            "ctl00$ContentPlaceHolder1$TextBox5": self.username,
            "ctl00$ContentPlaceHolder1$TextBox6": "",
            "ctl00$ContentPlaceHolder1$TextBox7": self.password,
            "ctl00$ContentPlaceHolder1$ButtonEtudiant": "Connexion",
            "ctl00$ContentPlaceHolder1$TextBox4": self.username,
            "ctl00$ContentPlaceHolder1$pass_parent": ""
        }
        response = self.session.post(url, data=data)
        
        # Check if login was successful
        print(colored("[+] Checking if the login was successful", "green"))
        if response.url.lower() == "https://esprit-tn.com/ESPOnline/Etudiants/Accueil.aspx".lower():
            print(colored("[+] Login successful", "green"))
        else:
            with open("login_failed.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            raise Exception(f"[-] Login failed: {response.url}, page content saved in login_failed.html")
    
    def getSess(self):
        response = self.session.get("https://esprit-tn.com/ESPOnline/Etudiants/Accueil.aspx")
        if response.url.lower() != "https://esprit-tn.com/ESPOnline/Etudiants/Accueil.aspx".lower():
            print(colored("[-] Please login again", "red"))
            return None
        return self.session
