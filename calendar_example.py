from esprit_tn import esprit
from termcolor import colored
from bs4 import BeautifulSoup
import json
from datetime import datetime
import fitz


def getCalendar(einst):
    loaded_session = einst.getSess()
    if loaded_session is None:
        return
    print(colored("[+] Going to calendar", "green"))
    url = "https://esprit-tn.com/esponline/Etudiants/Emplois.aspx"
    response = loaded_session.get(url)
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
                    print(colored("[-] Error parsing date", "red"))
            if "Emploi du temps Semaine" in cell.text:
                date_str = cell.text.split("Emploi du temps Semaine ")[1].split(".pdf")[0]
                try:
                    date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                    if date_obj > latest_date:
                        latest_date = date_obj
                        # Assuming the third column contains the <a> tag with the href
                        latest_href = cells[1].find("a")["href"]
                except ValueError:
                    print(colored("[-] Error parsing date", "red"))
    print(colored("[+] Latest timetable is: " + str(latest_date) + " with href " + latest_href, "green"))
    print(colored("[+] Downloading the latest timetable", "green"))
    data = {
        "__EVENTTARGET": latest_href.split("'")[1],
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
    }
    response = loaded_session.post(url, data=data)
    #search within the pdf for page that contains the classroom that we saved in the variable "classroom", and extract that page
    print(colored("[+] Timetable downloaded successfully, filtering...", "green"))
    with open("timetable.pdf", "wb") as f:
        f.write(response.content)
    pdf = fitz.open("timetable.pdf")
    output_pdf = fitz.open()
    for i in range(pdf.page_count):
        page_text = pdf[i].get_text("text")
        if classroom in page_text:
            output_pdf.insert_pdf(pdf, from_page=i, to_page=i)
            break
    if len(output_pdf) > 0:
        #output_pdf.save("filtered_timetable.pdf")
        pix = output_pdf[0].get_pixmap()
        pix.save("filtered_timetable.png")
        print(colored("[+] Filtered timetable saved as filtered_timetable.pdf", "green"))
    else:
        print(colored("[-] Couldn't find the classroom in the timetable", "red"))
    pdf.close()
    output_pdf.close()
    print(colored("[+] End of the script", "green"))

if __name__ == "__main__":
    with open("creds.json", "r") as f:
        creds = json.load(f)
    einst = esprit(creds["username"], creds["password"])
    einst.login()
    getCalendar(einst)
    