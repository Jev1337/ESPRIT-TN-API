import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
_USERNAME = ""
_PASSWORD = ""
def login(session):
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
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
        viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
    except TypeError:
        with open("login_failed.html", "w") as f:
            f.write(response.text)
        raise Exception("[-] Couldn't find the required fields, page content saved in login_failed.html")
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
    soup = BeautifulSoup(response.text, "html.parser")
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
    return response

@service
def esprit_check(action=None, id=None):
    sess = requests.Session()
    response = login(sess)
    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find("span", {"id": "Label2"})
    classroom = soup.find("span", {"id": "Label3"})
    if classroom is None:
        classroom = "Class Unavailable"
    else:
        classroom = classroom.text
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_name", value=name.text)
    
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_classroom", value=classroom)


@service
def esprit_get_marks(action=None, id=None):
    session = requests.Session()
    response = login(session)
    url = "https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx"
    response = task.executor(session.get, url)
    if response.url.lower() != "https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx".lower():
        return
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    if table is None:
        service.call("input_number", "set_value", entity_id="input_number.esprit_marks_avg", value=0)
        service.call("input_number", "set_value", entity_id="input_number.esprit_marks_nb", value=0)
        return
    rows = table.find_all("tr")
    tot = []
    for row in rows[1:]:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        tot += [cols]
        avg = 0
    totcoeff = 0
    failed = 0
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
        #Template: data["embed"]["fields"].append({"name": "Module "+ tot[i][0], "value": "Coeff: "+ tot[i][1] + "\nNote CC: "+ tot[i][3] + "\nNote TP: "+ tot[i][4] + "\nNote Examen: "+ tot[i][5], "inline": True})
        if (tot[i][3] != "" and tot[i][4] == "" and tot[i][5] != ""):
            avs = float(tot[i][3])*0.4 + float(tot[i][5])*0.6
            nb += avs
            if (avs < 8):
                failed += 1
            data["embed"]["fields"].append({"name": "Module "+ tot[i][0], "value": "Coeff: "+ tot[i][1] + "\nNote CC: "+ tot[i][3] + "\nNote Examen: "+ tot[i][5] + "\nAverage: "+ str(f"{avs:.2f}"), "inline": True})
        elif (tot[i][3] != "" and tot[i][4] != "" and tot[i][5] != ""):
            avs = float(tot[i][3])*0.3 + float(tot[i][4])*0.2 + float(tot[i][5])*0.5 
            nb += avs
            if (avs < 8):
                failed += 1
            data["embed"]["fields"].append({"name": "Module "+ tot[i][0], "value": "Coeff: "+ tot[i][1] + "\nNote CC: "+ tot[i][3] + "\nNote TP: "+ tot[i][4] + "\nNote Examen: "+ tot[i][5] + "\nAverage: "+ str(f"{avs:.2f}"), "inline": True})
        elif (tot[i][3] == "" and tot[i][4] == "" and tot[i][5] != ""):
            avs = float(tot[i][5])
            nb+= avs
            if (avs < 8):
                failed += 1
            data["embed"]["fields"].append({"name": "Module "+ tot[i][0], "value": "Coeff: "+ tot[i][1] + "\nNote Examen: "+ tot[i][5] + "\nAverage: "+ str(f"{avs:.2f}"), "inline": True})
        elif (tot[i][3] == "" and tot[i][4] != "" and tot[i][5] != ""):
            avs = float(tot[i][4])*0.2 + float(tot[i][5])*0.8
            nb += avs
            if (avs < 8):
                failed += 1
            data["embed"]["fields"].append({"name": "Module "+ tot[i][0], "value": "Coeff: "+ tot[i][1] + "\nNote TP: "+ tot[i][4] + "\nNote Examen: "+ tot[i][5] + "\nAverage: "+ str(f"{avs:.2f}"), "inline": True})
        avg += nb*coeff
    avg /= totcoeff
    data["embed"]["footer"]["text"] = "Average Marks: " + str(f"{avg:.2f}") + " | Total Returned Modules: " + str(len(tot)) + " | Failed Modules: " + str(failed) + " | ESPRIT-TN-API"
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
    classroom = soup.find("span", {"id": "Label3"})
    if classroom is None:
        classroom = "Class Unavailable"
    else:
        classroom = classroom.text
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
                        latest_href = cells[1].find("a")["href"]
                except ValueError:
                    log.error("Error parsing date")
            if "Emploi du temps Semaine" in cell.text:
                date_str = cell.text.split("Emploi du temps Semaine ")[1].split(".pdf")[0]
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                    if date_obj > latest_date:
                        latest_date = date_obj
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
    f = task.executor(os.open, f"www/timetable.pdf", os.O_RDWR | os.O_CREAT)
    task.executor(os.write, f, response.content)
    task.executor(os.close, f)
    k = task.executor(os.open, f"www/pdfdisplay.html", os.O_RDWR | os.O_CREAT)
    html = """
    <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
            <meta http-equiv="Pragma" content="no-cache" />
            <meta http-equiv="Expires" content="0" />
            <title>PDF Display</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js"></script>
            <style>
                #pdfContainer {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }
            </style>
        </head>
        <body>
            <div id="pdfContainer">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <script>
        function displayPDF() {
            const pdfPath = 'timetable.pdf';
            const searchText = '""" + classroom + """';
            pdfjsLib.getDocument(pdfPath).promise.then(function(pdf) {
                for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
                    pdf.getPage(pageNumber).then(function(page) {
                        page.getTextContent().then(function(textContent) {
                            if (textContent.items.some(item => item.str.includes(searchText))) {
                                const viewport = page.getViewport({ scale: 1.5 });
                                const canvas = document.createElement('canvas');
                                const context = canvas.getContext('2d');
                                canvas.height = viewport.height;
                                canvas.width = viewport.width;
                                document.getElementById('pdfContainer').appendChild(canvas);
                                page.render({ canvasContext: context, viewport: viewport });
                            }
                        });
                    });
                }
                document.getElementsByClassName('spinner-border')[0].remove();
                if (document.getElementById('pdfContainer').childElementCount === 0) {
                    document.getElementById('pdfContainer').innerHTML = 'Class not found in timetable';
                    document.getElementById('pdfContainer').style.color = 'red';
                    document.getElementById('pdfContainer').style.fontSize = '2rem';
                    document.getElementById('pdfContainer').style.fontWeight = 'bold';
                    document.getElementById('pdfContainer').style.textAlign = 'center';
                    document.getElementById('pdfContainer').style.display = 'flex';
                    document.getElementById('pdfContainer').style.justifyContent = 'center';
                    document.getElementById('pdfContainer').style.alignItems = 'center';
                    document.getElementById('pdfContainer').style.fontFamily = 'Arial, sans-serif';
                }
            });
        }   


                // Call the displayPDF function when the page loads
                window.onload = displayPDF;
            </script>
        </body>
        </html>
    """
    
    task.executor(os.write, k, html.encode('utf-8'))
    task.executor(os.close, k)
    service.call("notify", "dynobeta", message="", data={"embed": {"title": str(latest_date) + " Timetable", "description": "Here is the latest timetable for your classroom", "color": 145406, "url": "https://homeassistant.reps.tn/local/pdfdisplay.html", "author": {"name": "ESPRIT-TN-API", "url": "https://github.com/Jev1337/ESPRIT-TN-API"}, "footer": {}, "thumbnail": {"url": "https://i.imgur.com/lKDeVmh.png"}}}, target="1246109976485695639")