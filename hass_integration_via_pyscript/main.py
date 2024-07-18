import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import os

def login(session):
    _USERNAME = ""
    _PASSWORD = ""
    url = "https://esprit-tn.com/esponline/Online/default.aspx"
    response = task.executor(session.get, url)
    soup = BeautifulSoup(response.text, "html.parser")
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        "ctl00$ContentPlaceHolder1$TextBox1": "",
        "ctl00$ContentPlaceHolder1$TextBox5": "",
        "ctl00$ContentPlaceHolder1$TextBox6": "",
        "ctl00$ContentPlaceHolder1$TextBox3": _USERNAME,
        "ctl00$ContentPlaceHolder1$Button3": "Suivant",
        "ctl00$ContentPlaceHolder1$TextBox4": _USERNAME,
        "ctl00$ContentPlaceHolder1$pass_parent": _PASSWORD,
    }
    response = task.executor(session.post, url, data=data)
    try:
        viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
        viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    except TypeError:
        with open("login_failed.html", "w") as f:
            f.write(response.text)
        raise Exception("[-] Couldn't find the required fields, page content saved in login_failed.html")
    soup = BeautifulSoup(response.text, "html.parser")
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        "ctl00$ContentPlaceHolder1$TextBox1": "",
        "ctl00$ContentPlaceHolder1$TextBox5": _USERNAME,
        "ctl00$ContentPlaceHolder1$TextBox6": "",
        "ctl00$ContentPlaceHolder1$TextBox7": _PASSWORD,
        "ctl00$ContentPlaceHolder1$ButtonEtudiant": "Connexion",
        "ctl00$ContentPlaceHolder1$TextBox4": _USERNAME,
        "ctl00$ContentPlaceHolder1$pass_parent": ""
    }
    response = task.executor(session.post, url, data=data)
    try:
        viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
        viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    except TypeError:
        with open("login_failed.html", "w") as f:
            f.write(response.text)
        raise Exception("[-] Couldn't find the required fields, page content saved in login_failed.html")
    if response.url.lower() == "https://esprit-tn.com/ESPOnline/Etudiants/Accueil.aspx".lower():
        log.info("Successfully Logged In!")
    else:
        log.error("Error Logging In!")
        raise Exception(f"[-] Login failed: {response.url}, page content saved in login_failed.html")

@service
def esprit_check(action=None, id=None):
    sess = requests.Session()
    login(sess)
    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find("span", {"id": "Label2"})
    classroom = soup.find("span", {"id": "Label3"})
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_name", value=name.text)
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_classroom", value=classroom.text)

    url = "https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx"
    response = task.executor(session.get, url)
    if response.url.lower() != "https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx".lower():
        return
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    rows = table.find_all("tr")
    tot = []

    #Using the marks, we calculate the average by using this js formula:


    for row in rows[1:]:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        tot += [cols]
        avg = 0
    totcoeff = 0
    data=   {"embed": { "title": "Returned Modules for " + _USERNAME, 
                        "description": "@everyone Grades have been updated!", 
                        "color": 145406,
                        "url":"https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx", 
                        "author": {"name": "ESPRIT-TN-API", 
                                    "url" : "https://github.com/Jev1337/ESPRIT-TN-API"} , 
                        "footer": {}, 
                        "thumbnail":{ "url": "https://i.imgur.com/lKDeVmh.png"}, 
                        "fields" : []
                        }
            }
    for i in range(len(tot)):
        tot[i] = [x.replace(",", ".") for x in tot[i]]
        coeff = float(tot[i][1])
        totcoeff += coeff
        nb = 0
        data["embed"]["fields"].append({"name": "Module "+ tot[i][0], "value": "Coeff: "+ tot[i][1] + "\nNote CC: "+ tot[i][3] + "\nNote TP: "+ tot[i][4] + "\nNote Examen: "+ tot[i][5] , "inline": True})
        if (tot[i][3] != "" and tot[i][4] == "" and tot[i][5] != ""):
            nb += float(tot[i][3])*0.4 + float(tot[i][5])*0.6
        elif (tot[i][3] != "" and tot[i][4] != "" and tot[i][5] != ""):
            nb += float(tot[i][3])*0.3 + float(tot[i][4])*0.2 + float(tot[i][5])*0.5
        elif (tot[i][3] == "" and tot[i][4] == "" and tot[i][5] != ""):
            nb+= float(tot[i][5])
        elif (tot[i][3] == "" and tot[i][4] != "" and tot[i][5] != ""):
            
            nb += float(tot[i][4])*0.2 + float(tot[i][5])*0.8
        avg += nb*coeff
    avg /= totcoeff
    data["embed"]["footer"]["text"] = "Average Marks: " + str(f"{avg:.2f}") + " | Total Returned Modules: " + str(len(tot)) + " | By Jev1337"
    if int(float(input_number.esprit_marks_nb)) != len(tot):
        service.call("notify", "dynobeta", message="", data=data, target="1246109976485695639")
        
    service.call("input_number", "set_value", entity_id="input_number.esprit_marks_avg", value=avg)
    service.call("input_number", "set_value", entity_id="input_number.esprit_marks_nb", value=len(tot))
    
    
@service
def esprit_get_timetable(action=None, id=None):
    session = requests.Session()
    login(session)
    url = "https://esprit-tn.com/esponline/Etudiants/Emplois.aspx"
    response = task.executor(session.get, url)
    soup = BeautifulSoup(response.text, "html.parser")
    classroom = soup.find("span", {"id": "Label3"}).text
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    rows = table.find_all("tr")

    latest_date = datetime.min
    latest_href = ""
    for row in rows:
        cells = row.find_all("td")
        for cell in cells:
            if "emploi du temps semaine du" in cell.text:
                date_str = cell.text.split("emploi du temps semaine du  ")[1].split(".pdf")[0]
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                    if date_obj > latest_date:
                        latest_date = date_obj
                        # Assuming the third column contains the <a> tag with the href
                        latest_href = cells[1].find("a")["href"]
                except ValueError:
                    log.error("Error parsing date")
            if "Emploi du temps Semaine" in cell.text:
                date_str = cell.text.split("Emploi du temps Semaine ")[1].split(".pdf")[0]
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                    if date_obj > latest_date:
                        latest_date = date_obj
                        # Assuming the third column contains the <a> tag with the href
                        latest_href = cells[1].find("a")["href"]
                except ValueError:
                    log.error("Error parsing date")
    log.info(f"Latest timetable is: {latest_date} with href {latest_href}")
    data = {
        "__EVENTTARGET": latest_href.split("'")[1],
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
    }
    response = task.executor(session.post, url, data=data)
    f = task.executor(os.open, f"www/local/timetable_{classroom}.pdf", os.O_RDWR | os.O_CREAT)
    task.executor(os.write, f, response.content)
    