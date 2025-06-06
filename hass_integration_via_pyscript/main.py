import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import re

_USERNAME = ""
_PASSWORD = ""

def login(session):
    url = "https://esprit-tn.com/esponline/Online/default.aspx"
    response = task.executor(session.get, url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
    viewstategenerator_tag = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
    eventvalidation_tag = soup.find("input", {"name": "__EVENTVALIDATION"})
    if not (viewstate_tag and viewstategenerator_tag and eventvalidation_tag):
        log.error("Missing one of the required fields (__VIEWSTATE, __VIEWSTATEGENERATOR, or __EVENTVALIDATION).")
        return
    
    # Check if we need to handle the "I'm not a robot" checkbox
    checkbox = soup.find("input", {"name": "ctl00$ContentPlaceHolder1$chkImage"})
    if checkbox:
        log.info("Found 'I'm not a robot' checkbox, checking it first")
        data = {
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$chkImage",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": viewstate_tag["value"],
            "__VIEWSTATEGENERATOR": viewstategenerator_tag["value"],
            "__EVENTVALIDATION": eventvalidation_tag["value"],
            "ctl00$ContentPlaceHolder1$TextBox1": "",
            "ctl00$ContentPlaceHolder1$TextBox5": "",
            "ctl00$ContentPlaceHolder1$TextBox6": "",
            "ctl00$ContentPlaceHolder1$TextBox3": "",
            "ctl00$ContentPlaceHolder1$TextBox4": "",
            "ctl00$ContentPlaceHolder1$pass_parent": "",
            "ctl00$ContentPlaceHolder1$chkImage": "on"  # Explicitly check the checkbox
        }
        response = task.executor(session.post, url, data=data)
        soup = BeautifulSoup(response.text, "html.parser")
        
        viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
        viewstategenerator_tag = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
        eventvalidation_tag = soup.find("input", {"name": "__EVENTVALIDATION"})
        if not (viewstate_tag and viewstategenerator_tag and eventvalidation_tag):
            log.error("Missing one of the required fields after checkbox.")
            return
    
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate_tag["value"],
        "__VIEWSTATEGENERATOR": viewstategenerator_tag["value"],
        "__EVENTVALIDATION": eventvalidation_tag["value"],
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
    
    viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
    viewstategenerator_tag = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
    eventvalidation_tag = soup.find("input", {"name": "__EVENTVALIDATION"})
    if not (viewstate_tag and viewstategenerator_tag and eventvalidation_tag):
        log.error("Missing one of the required fields (second phase).")
        return
    
    data = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate_tag["value"],
        "__VIEWSTATEGENERATOR": viewstategenerator_tag["value"],
        "__EVENTVALIDATION": eventvalidation_tag["value"],
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
    
    viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
    viewstategenerator_tag = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
    eventvalidation_tag = soup.find("input", {"name": "__EVENTVALIDATION"})
    if not (viewstate_tag and viewstategenerator_tag and eventvalidation_tag):
        log.error("Missing one of the required fields (third phase).")
        return
    
    if response.url.lower() == "https://esprit-tn.com/ESPOnline/Etudiants/Accueil.aspx".lower():
        log.info("Successfully Logged In!")
    else:
        log.error("Error Logging In!")
        return
    return response

@service
def esprit_check(action=None, id=None):
    sess = requests.Session()
    response = login(sess)
    if not response:
        return
    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find("span", {"id": "Label2"})
    classroom = soup.find("span", {"id": "Label3"})
    if classroom is None:
        classroom = "Class Unavailable"
    else:
        classroom = classroom.text
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_name", value=name.text if name else "")
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_classroom", value=classroom)
    service.call("input_text", "set_value", entity_id="input_text.last_run_status", value="Checked ESPRIT Info at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("Successfully checked ESPRIT info!")

@service
def esprit_get_marks(action=None, id=None):
    session = requests.Session()
    response = login(session)
    if not response:
        return
    url = "https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx"
    response = task.executor(session.get, url)
    if response.url.lower() != "https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx".lower():
        return
    
    # ESPRIT CHECK BLOCK
    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find("span", {"id": "Label2"})
    classroom = soup.find("span", {"id": "Label3"})
    if classroom is None:
        classroom = "Class Unavailable"
    else:
        classroom = classroom.text
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_name", value=name.text if name else "")
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_classroom", value=classroom)
    # END OF ESPRIT CHECK BLOCK

    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    if table is None:
        if datetime.now().month == 9:
            service.call("input_number", "set_value", entity_id="input_number.esprit_marks_avg", value=0)
            service.call("input_number", "set_value", entity_id="input_number.esprit_marks_nb", value=0)
            service.call("input_text", "set_value", entity_id="input_text.last_run_status", value="[RZ] Checked ESPRIT Marks at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            log.info("Successfully checked ESPRIT marks! Reset allowed.")
        else:
            service.call("input_text", "set_value", entity_id="input_text.last_run_status", value="[NRZ] Checked ESPRIT Marks at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            log.info("Successfully checked ESPRIT marks! Prevented reset due to month.")
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
        service.call("notify", "dynobeta", message="@everyone", data=data, target="1246109976485695639")
    service.call("input_number", "set_value", entity_id="input_number.esprit_marks_avg", value=avg)
    service.call("input_number", "set_value", entity_id="input_number.esprit_marks_nb", value=len(tot))
    service.call("input_text", "set_value", entity_id="input_text.last_run_status", value="Checked ESPRIT Marks at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("Successfully checked ESPRIT marks!")

@service
def esprit_get_timetable(action=None, id=None):
    session = requests.Session()
    if not login(session):
        return
    url = "https://esprit-tn.com/esponline/Etudiants/Emplois.aspx"
    response = task.executor(session.get, url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    classroom = soup.find("span", {"id": "Label3"})
    if classroom is None:
        classroom = "Class Unavailable"
    else:
        classroom = classroom.text

    first_space_index = classroom.find(" ")
    classroom = classroom.replace(" ", "", 1)
    classroom = re.sub(r"\s+", "", classroom)
    
    match = re.search(r"[1-5][A-Z]+-?[A-Z]*[0-9]{0,2}", classroom)
    if match:
        classroom = match.group(0)
    if first_space_index != -1:
        classroom = classroom[:first_space_index] + " " + classroom[first_space_index:]
    service.call("input_text", "set_value", entity_id="input_text.esprit_user_classroom", value=classroom)

    viewstate_tag = soup.find("input", {"name": "__VIEWSTATE"})
    eventvalidation_tag = soup.find("input", {"name": "__EVENTVALIDATION"})
    viewstategenerator_tag = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})
    
    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    if not (viewstate_tag and eventvalidation_tag and viewstategenerator_tag and table):
        log.error("Missing required timetable fields.")
        return
    
    rows = table.find_all("tr")
    latest_date = datetime.min
    latest_href = ""
    for row in rows:
        cells = row.find_all("td")
        for cell in cells:
            if "semaine" in cell.text.lower():
                match_date = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{8})", cell.text)
                if match_date:
                    date_str = match_date.group(0)
                    try:
                        if "-" in date_str:
                            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                        elif "/" in date_str:
                            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                        else:
                            date_obj = datetime.strptime(date_str, "%d%m%Y")
                        if date_obj > latest_date:
                            latest_date = date_obj
                            link = cells[1].find("a")
                            if link and link.get("href"):
                                latest_href = link["href"]
                    except:
                        log.error("Error parsing date.")
    
    log.info(f"Latest timetable is: {latest_date} with href {latest_href}")
    data = {
        "__EVENTTARGET": latest_href.split("'")[1] if latest_href else "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate_tag["value"],
        "__VIEWSTATEGENERATOR": viewstategenerator_tag["value"],
        "__EVENTVALIDATION": eventvalidation_tag["value"],
    }
    timetable_response = task.executor(session.post, url, data=data)
    today = datetime.now().strftime("%Y-%m-%d")
    for file in os.listdir("www"):
        if file.startswith("timetable_") and file.endswith(".pdf"):
            os.remove(f"www/{file}")
    f = task.executor(os.open, f"www/timetable_{today}.pdf", os.O_RDWR | os.O_CREAT)
    task.executor(os.write, f, timetable_response.content)
    task.executor(os.close, f)
    k = task.executor(os.open, "www/pdfdisplay.html", os.O_RDWR | os.O_CREAT)
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
            <meta http-equiv="Pragma" content="no-cache" />
            <meta http-equiv="Expires" content="0" />
            <title>PDF Display</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js"></script>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <style>
                html, body {
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    overflow-x: hidden;
                }
                #pdfContainer {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    min-height: 100vh;
                    padding-top: 5rem;
                }
                canvas {
                    max-width: 90%;
                    height: auto;
                }
            </style>
        </head>
        <body>
            <a href="javascript:window.location.reload();" class="btn btn-primary position-absolute top-0 end-0 m-3">
                <i class="fa fa-refresh fa-spin"></i>
            </a>
            <div id="pdfContainer">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <script>
                async function displayPDF() {
                    const pdfPath = 'timetable_""" + today + """.pdf';
                    const searchText = '""" + classroom + """';
                    const pdfContainer = document.getElementById('pdfContainer');
                    const loadingSpinner = document.getElementsByClassName('spinner-border')[0];
                    try {
                        var text_to_search = searchText;
                        if (text_to_search[text_to_search.length - 1] >= '0' && text_to_search[text_to_search.length - 1] <= '9') {
                            text_to_search += "0";
                        }
                        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                        const pdfData = await fetch(pdfPath).then(response => response.arrayBuffer());
                        const pdf = await pdfjsLib.getDocument({ data: pdfData }).promise;
                        let classFound = false;
                        const scale = 1.0;

                        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
                            const page = await pdf.getPage(pageNumber);
                            const textContent = await page.getTextContent();
                            if (textContent.items.map(item => item.str).join('').includes(text_to_search)) {
                                classFound = true;
                                const viewport = page.getViewport({ scale: scale });
                                const canvas = document.createElement('canvas');
                                const context = canvas.getContext('2d');
                                canvas.height = viewport.height;
                                canvas.width = viewport.width;
                                pdfContainer.appendChild(canvas);
                                await page.render({ canvasContext: context, viewport: viewport }).promise;
                            }
                            if (classFound) break;
                        }
                        loadingSpinner.remove();

                        if (!classFound) {
                            pdfContainer.innerHTML = 'Class not found in timetable';
                            pdfContainer.style.color = 'red';
                            pdfContainer.style.fontSize = '2rem';
                            pdfContainer.style.fontWeight = 'bold';
                            pdfContainer.style.textAlign = 'center';
                            pdfContainer.style.display = 'flex';
                            pdfContainer.style.justifyContent = 'center';
                            pdfContainer.style.alignItems = 'center';
                            pdfContainer.style.fontFamily = 'Arial, sans-serif';
                        }
                    } catch (error) {
                        console.error('Error loading PDF:', error);
                        loadingSpinner.remove();
                        pdfContainer.innerHTML = 'Error loading PDF';
                        pdfContainer.style.color = 'red';
                        pdfContainer.style.textAlign = 'center';
                    }
                }
                window.onload = displayPDF;
            </script>
        </body>
    </html>
    """
    task.executor(os.write, k, html.encode('utf-8'))
    task.executor(os.close, k)
    service.call("notify", "dynobeta", message="", data={
        "embed": {
            "title": str(latest_date) + " Timetable",
            "description": "Here is the latest timetable for your classroom",
            "color": 145406,
            "url": "https://homeassistant.reps.tn/local/pdfdisplay.html",
            "author": {"name": "ESPRIT-TN-API", "url": "https://github.com/Jev1337/ESPRIT-TN-API"},
            "footer": {},
            "thumbnail": {"url": "https://i.imgur.com/lKDeVmh.png"}
        }
    }, target="1246109976485695639")
    service.call("input_text", "set_value", entity_id="input_text.last_run_status", value="Checked ESPRIT Timetable at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("Successfully checked ESPRIT timetable!")