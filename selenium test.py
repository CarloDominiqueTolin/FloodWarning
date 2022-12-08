from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

pagasa_link = 'http://121.58.193.173:8080/'
pages = ['water/table.do','rainfall/table.do']

#print(browser.find_element(By.CLASS_NAME,'year').get_attribute('innerHTML'))
#print(BeautifulSoup(browser.find_element(By.CLASS_NAME,'year')))
def generateReportLog(date ,location, dfInfo):
    with open(r"pagasaFetchLog","a") as f:
        f.write(info)


def dateValue():
    formatDate = "%B/%d/%Y/%H:%M"
    tmp = browser.find_element(By.CLASS_NAME,'dtpicker-value').text
    tmp = '/'.join([x.strip(',') for x in tmp.split()[1::]])
    return dt.datetime.strptime(tmp, formatDate)


def resetDateInput(browser, startDate=dt.datetime(2011,10,29,00,00)):
    browser.find_element(By.CLASS_NAME,'btn-icon').click()
    
    tmp = browser.find_element(By.CLASS_NAME,'minutes')
    while dateValue().minute != 00:
        tmp.find_element(By.CLASS_NAME, "decrement").click()
      
    tmp = browser.find_element(By.CLASS_NAME,'hour')
    while dateValue().hour != 00:
        tmp.find_element(By.CLASS_NAME, "decrement").click()
    
    tmp = browser.find_element(By.CLASS_NAME,'day')
    while dateValue().day != startDate.day:
        tmp.find_element(By.CLASS_NAME, "decrement").click()

    tmp = browser.find_element(By.CLASS_NAME,'month')
    while dateValue().month != startDate.month:
        tmp.find_element(By.CLASS_NAME, "decrement").click()
    
    tmp = browser.find_element(By.CLASS_NAME,'year')
    while dateValue().year != startDate.year:
        if dateValue().year > startDate.year:
            tmp.find_element(By.CLASS_NAME, "decrement").click()
        else:
            tmp.find_element(By.CLASS_NAME, "increment").click()

    browser.find_element(By.CLASS_NAME,'dtpicker-buttonSet').click()
    browser.find_element(By.CLASS_NAME,'btn-search').click()


def setDateInput(browser):
    browser.find_element(By.CLASS_NAME,'btn-icon').click()
    tmp = browser.find_element(By.CLASS_NAME,'day')
    tmp.find_element(By.CLASS_NAME, "increment").click()
    browser.find_element(By.CLASS_NAME,'dtpicker-buttonSet').click()
    browser.find_element(By.CLASS_NAME,'btn-search').click()

    
def getDailyTable(browser,targetData):
    tmp2 = browser.find_element(By.CLASS_NAME, "content-view-left")
    tmp2 = browser.find_element(By.CLASS_NAME, "dataList")
    all_ID = tmp2.find_elements(By.TAG_NAME, "tr")

    locationID = [i.get_attribute("id") for i in all_ID]
    date = browser.find_element(By.ID,'searchtime').get_attribute("value").split()[0]

    output = pd.DataFrame({'time':[],'location':[],'waterLevel':[]})
    for locID in locationID:
        tmp2.find_element(By.ID, locID).click()

        tmp = browser.find_element(By.CLASS_NAME, "content-view-right")

        x = tmp.find_element(By.ID, "detailTable").get_attribute('innerHTML')
        soup = BeautifulSoup(x,features="html.parser")

        features = {'time':[],'location':[],'waterLevel':[]}
        location = list(soup.caption.children)[0].split()[-1]
        print(targetData, date, location)
    
        for row in soup.find_all('tr')[1::]:
            y = row.find_all('span')
            features['time'].append(y[0].get_text())
            features['location'].append(location)
            features['waterLevel'].append(y[1].get_text())

        output = pd.concat([output,pd.DataFrame(features)],ignore_index=True)
        
    return output


if __name__ == "__main__":
    browser = webdriver.Chrome()
    browser.get(pagasa_link+pages[0])
    
    resetDateInput(browser)

    dataset = pd.DataFrame({'time':[],'location':[],'waterLevel':[]})
    
    startDate = dt.datetime(2011,10,29,00,00)
    endDate = dt.datetime.now()

    while True:
        try: 
            for i in range(365): #(endDate-startDate).days-1    
                dataset = pd.concat([dataset,getDailyTable(browser,'water-level')],ignore_index=True)
                setDateInput(browser)
            break
        except Exception as e:
            print('!!!!!!!!!!\n',e,'\n!!!!!!!!!!')
            
            
    print(dataset.info())
    #input("\nSave to csv File??")
    dataset.to_csv('pagasa.csv', index=False)

    
    
    
