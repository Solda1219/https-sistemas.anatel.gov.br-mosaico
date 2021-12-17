from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
from bs4 import BeautifulSoup
import csv

url='https://sistemas.anatel.gov.br/mosaico/sch/publicView/listarProdutosHomologados.xhtml'
requester = "HARMAN DO BRASIL INDUSTRIA ELETRONICA E PARTICIPACOES LTDA."
TIMEOUT = 50

def getPageNum(str):
    str = str.strip(')') # remove last character ')'
    list = str.split()
    page_num = list[-1]
    print(page_num)
    if page_num.isnumeric():
        return int(page_num)
    else:
        return 0

class SCHScraper:
    def __init__(self, url):
        self.url = url

    def scrap_by_requester(self, requester):
        options = Options()
        options.headless = False
        options.add_argument("--window-size=1920,1200")
        driver = webdriver.Chrome(options=options, executable_path="chromedriver.exe")

        driver.get(self.url)
        time.sleep(3)
        driver.find_element_by_id("listarProdutosForm:j_idt62_input").send_keys(requester) # set Request
        time.sleep(3)
        driver.find_element_by_id("listarProdutosForm:j_idt62_input").click()
        time.sleep(5)
        driver.find_element_by_xpath("//li[@class='ui-autocomplete-item ui-autocomplete-list-item ui-corner-all ui-state-highlight']").click()
        time.sleep(3)
        filter = driver.find_element_by_id("listarProdutosForm:j_idt106").click() # click filter button
        time.sleep(TIMEOUT)
        
        ## set record_num 100 
        driver.find_element_by_xpath("//select[@class='ui-paginator-rpp-options ui-widget ui-state-default ui-corner-left']").send_keys(100)

        time.sleep(TIMEOUT)

        ## get page_num
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        pagenation = soup.find('span', attrs={'class':'ui-paginator-current'})
        page_num = getPageNum(pagenation.text) #(Registro: 1 - 100 de 52909, Página: 1 de 530)

        driver.find_element_by_xpath("//span[@class='ui-paginator-next ui-state-default ui-corner-all']").click()
        time.sleep(TIMEOUT)
        for i in range(0, page_num):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            tbody = soup.find('tbody', attrs={'id':'listarProdutosForm:tableHomologados_data'})
            # print(tbody)

            total = []
            for info in tbody.find_all('tr', attrs={'role':'row'}):
                index = 0
                new = []
                for item in info.find_all("td", attrs={'role':'gridcell'}):
                    if index == 0:
                        s = item.find("a")
                    elif index >= 5:
                        break
                    else:
                        s = item.find("div")
                    # print(s)
                    # print('\n')
                    new.append(s.text.strip())
                    index +=1
                total.append(new)

            ## save datas in csv
            df = pd.DataFrame(total, columns=['no','Product Model', 'Manufacture', 'Product Type', 'Self life'])
            df.to_csv('result.csv', mode='a', header=False, index=False, encoding='utf-8')

            if i == page_num-1:
                print('end')
                break
            ## click next button
            print(i)
            driver.find_element_by_xpath("//span[@class='ui-paginator-next ui-state-default ui-corner-all']").click()
            time.sleep(TIMEOUT)
        driver.quit()

if __name__ == '__main__':
    scraper = SCHScraper(url)
    scraper.scrap_by_requester(requester)
