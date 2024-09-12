import requests
from bs4 import BeautifulSoup


url = "https://www.fatourati.ma/FatLite/ma/MTC/formulaire?cid=01&fid=1039"


def scrape_data(num_contrat):
    payload = {
        "cid": "01",
        "fid": "1039",
        "refTransac": "",
        "paymentType": "1",
        "cbType": "0",
        "num_contrat": num_contrat,
        "email": "a@a.com",
        "email1": "a@a.com",
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        return {"error": "Failed to scrape data"}

    soup = BeautifulSoup(response.text, 'html.parser')
    # Example: Extract the title (customize as per your scraping logic)
    title = soup.title.string if soup.title else "No title"

    # Return the data as JSON (customize this based on your needs)
    return {"title": title, "status": "success"}

