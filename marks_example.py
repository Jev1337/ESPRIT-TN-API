from esprit_tn import esprit
from termcolor import colored
from bs4 import BeautifulSoup
import json



def getMarks(einst):
    loaded_session = einst.getSess()
    if loaded_session is None:
        return
    print(colored("[+] Going to the result page", "green"))
    url = "https://esprit-tn.com/ESPOnline/Etudiants/Resultat2021.aspx"
    response = loaded_session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "ContentPlaceHolder1_GridView1"})
    rows = table.find_all("tr")
    tot = []
    for row in rows[1:]:
        cols = row.find_all("td")
        cols = [ele.text.strip() for ele in cols]
        tot += [cols]
    avg = 0
    totcoeff = 0
    failed = 0
    for i in range(len(tot)):
        tot[i] = [x.replace(",", ".") for x in tot[i]]
        coeff = float(tot[i][1])
        totcoeff += coeff
        nb = 0
        if (tot[i][3] != "" and tot[i][4] == "" and tot[i][5] != ""):
            nb += float(tot[i][3])*0.4 + float(tot[i][5])*0.6
            if (float(tot[i][3])*0.4 + float(tot[i][5])*0.6 < 8):
                failed += 1
        elif (tot[i][3] != "" and tot[i][4] != "" and tot[i][5] != ""):
            nb += float(tot[i][3])*0.3 + float(tot[i][4])*0.2 + float(tot[i][5])*0.5
            if (float(tot[i][3])*0.3 + float(tot[i][4])*0.2 + float(tot[i][5])*0.5 < 8):
                failed += 1
        elif (tot[i][3] == "" and tot[i][4] == "" and tot[i][5] != ""):
            nb+= float(tot[i][5])
            if (float(tot[i][5]) < 8):
                failed += 1
        elif (tot[i][3] == "" and tot[i][4] != "" and tot[i][5] != ""):
            nb += float(tot[i][4])*0.2 + float(tot[i][5])*0.8
            if (float(tot[i][4])*0.2 + float(tot[i][5])*0.8 < 8):
                failed += 1
        avg += nb*coeff
    avg /= totcoeff
    print(colored("[+] You failed " + str(failed) + " modules", "green"))
    print(colored("[+] Your average is: " + str(avg), "green"))
    print(colored("[+] Your total coefficient is: " + str(totcoeff), "green"))
    print(colored("[+] Your marks are: ", "green"))
    for i in tot:
        print(i)
    print(colored("[+] End of the script", "green"))

if __name__ == "__main__":
    with open("creds.json", "r") as f:
        creds = json.load(f)
    einst = esprit(creds["username"], creds["password"])
    einst.login()
    getMarks(einst)
    