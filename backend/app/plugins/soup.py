from bs4 import BeautifulSoup
import requests 

class Soup:
    def __init__(self, url):
        self.url = url
        r = requests.get(url) 
        self.soup = BeautifulSoup(r.text, 'html.parser')
    
    def governance_info(self):
        title = self.soup.title.name
        return {
            'id': self.url,
            'name': title
        }
    
    def legal_act_info(self):
        date = self.soup.find("div", {"id": "act:currency"}).find('td', {"class": "currencysingle"}).get_text()
        title = self.soup.find("div", {"id": "title"}).find('h2').get_text()
        return {
            'id': self.url,
            'name': title,
            'date': date.split('current to')[-1].strip()
        }