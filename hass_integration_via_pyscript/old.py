import requests
import json
from bs4 import BeautifulSoup



@service
def esprit_check(action=None, id=None):
    _USERNAME = ""
    _PASSWORD = ""
    session = requests.Session()
    url = "https://esprit-tn.com/esponline/Online/default.aspx"
    response = task.executor(session.get, url)
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": "/wEPDwUJNDE1NjEwODA3D2QWAmYPZBYCAgMPZBYCAgUPDxYCHgRUZXh0BQkyMDIzLzIwMjRkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUSY3RsMDAkSW1hZ2VCdXR0b24xICMZk+ouPK+JTfNlRJ2sscAzybqvxqLnJuWoAXjvdLE=",
        "__VIEWSTATEGENERATOR": "717FCBFE",
        "__EVENTVALIDATION": "/wEdAA1A5Yy0pFuepMJZDAUwICeMD4zZrxX92uOlyIx1SyGTQokHj7KsGQZ9KI/q0cgR79eMO7fmjkJSfq6Zbgk2kTWn5BPdHG87XtyblNclsuAS8LvwPnslbtZbTzH+LM3KrmKoScikkrtCyMBYLZBZxv2YCNTGu6fpAlK5HiRhQ3QX7uQuDNsn18Vb/yPhT9ZPmVoNeSKFy2zxLVV4+zExdQxF5O2yeRHTM5Q6txDv+t953Rsahgpohlzzax1rmqU36I8bifdujSibODz2lHN+RHz6GF0hbOj1aCMe8X0CT1Q5QWzBhzv4Ktr7BS9U08abXRg=",
        "ctl00$ContentPlaceHolder1$TextBox1": "",
        "ctl00$ContentPlaceHolder1$TextBox5": "",
        "ctl00$ContentPlaceHolder1$TextBox6": "",
        "ctl00$ContentPlaceHolder1$TextBox3": _USERNAME,
        "ctl00$ContentPlaceHolder1$Button3": "Suivant",
        "ctl00$ContentPlaceHolder1$TextBox4": _USERNAME,
        "ctl00$ContentPlaceHolder1$pass_parent": _PASSWORD,
    }
    response = task.executor(session.post, url, data=data)
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": "/wEPDwUJNDE1NjEwODA3D2QWAmYPZBYCAgMPZBYEAgUPDxYCHgRUZXh0BQkyMDIzLzIwMjRkZAIHD2QWAgIND2QWEAIBDw8WAh4HVmlzaWJsZWhkZAIDDw8WBB8ABQoyMTFKTVQ1MzgwHwFoZGQCBw8PFgIfAWdkZAIJDw8WAh8BZ2RkAgsPDxYCHgdFbmFibGVkZ2RkAg0PDxYCHwFnZGQCDw8PFgIfAWdkZAIRDw8WAh8BaGRkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBRJjdGwwMCRJbWFnZUJ1dHRvbjHiffVuzYh2Bcroz3oFZzfjNrPWy135OdJTLGw7f/mHcg==",
        "__VIEWSTATEGENERATOR": "717FCBFE",
        "__EVENTVALIDATION": "/wEdAA7/7YkHtfZhBiBKI8qicTvOD4zZrxX92uOlyIx1SyGTQokHj7KsGQZ9KI/q0cgR79eMO7fmjkJSfq6Zbgk2kTWn5BPdHG87XtyblNclsuAS8LvwPnslbtZbTzH+LM3KrmKoScikkrtCyMBYLZBZxv2Y4YHt2yH9TCYlNrTCCQccHuaXknurQIHyJEMAivskpdkfOLtcwEziInaQqEgDH0GiDXkihcts8S1VePsxMXUMReTtsnkR0zOUOrcQ7/rfed0bGoYKaIZc82sda5qlN+iPG4n3bo0omzg89pRzfkR8+go6VS8juKrBQqchUBkHW0Ohkx9NP2NjG7jwEQGSYKzB",
        "ctl00$ContentPlaceHolder1$TextBox1": "",
        "ctl00$ContentPlaceHolder1$TextBox5": _USERNAME,
        "ctl00$ContentPlaceHolder1$TextBox6": "",
        "ctl00$ContentPlaceHolder1$TextBox7": _PASSWORD,
        "ctl00$ContentPlaceHolder1$ButtonEtudiant": "Connexion",
        "ctl00$ContentPlaceHolder1$TextBox4": _USERNAME,
        "ctl00$ContentPlaceHolder1$pass_parent": ""
    }
    response = task.executor(session.post, url, data=data)
    if response.url.lower() == "https://esprit-tn.com/ESPOnline/Etudiants/Accueil.aspx".lower():
        log.info("Successfully Logged In!")
    else:
        log.error("Error Logging In!")
        return
    #get span content with id label2
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
    
    
