from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import  selenium.webdriver.support.expected_conditions as ec
from bs4 import BeautifulSoup
import pyarrow.feather as feather
import pandas as pd
import datetime as dt
import calendar

pagasa_link = 'http://121.58.193.173:8080/'
pages = ['water/table.do','rainfall/table.do']
headings = {'date':[],'time':[],'location':[],'waterLevel':[]}

#print(browser.find_element(By.CLASS_NAME,'year').get_attribute('innerHTML'))
#print(BeautifulSoup(browser.find_element(By.CLASS_NAME,'year')))
def generateReportLog(date ,location, dfInfo):
    with open(r"pagasaFetchLog","a") as f:
        f.write(info)


def dateValue(browser):
    formatDate = "%B/%d/%Y/%H:%M"
    tmp = browser.find_element(By.CLASS_NAME,'dtpicker-value').text
    tmp = '/'.join([x.strip(',') for x in tmp.split()[1::]])
    return dt.datetime.strptime(tmp, formatDate)


def goToDate(browser, startDate=dt.datetime(2011,10,29,00,00)):
    browser.find_element(By.CLASS_NAME,'btn-icon').click()
    
    tmp = browser.find_element(By.CLASS_NAME,'minutes')
    while dateValue(browser).minute != 00:
        tmp.find_element(By.CLASS_NAME, "decrement").click()
      
    tmp = browser.find_element(By.CLASS_NAME,'hour')
    while dateValue(browser).hour != 00:
        tmp.find_element(By.CLASS_NAME, "decrement").click()
    
    tmp = browser.find_element(By.CLASS_NAME,'year')
    while dateValue(browser).year != startDate.year:
        if dateValue(browser).year > startDate.year:
            tmp.find_element(By.CLASS_NAME, "decrement").click()
        else:
            tmp.find_element(By.CLASS_NAME, "increment").click()

    tmp = browser.find_element(By.CLASS_NAME,'month')
    while dateValue(browser).month != startDate.month:
        if dateValue(browser).month > startDate.month:
            tmp.find_element(By.CLASS_NAME, "decrement").click()
        else:
            tmp.find_element(By.CLASS_NAME, "increment").click()

    tmp = browser.find_element(By.CLASS_NAME,'day')
    while dateValue(browser).day != startDate.day:
        if dateValue(browser).day > startDate.day:
            tmp.find_element(By.CLASS_NAME, "decrement").click()
        else:
            tmp.find_element(By.CLASS_NAME, "increment").click()

    browser.find_element(By.CLASS_NAME,'dtpicker-buttonSet').click()
    browser.find_element(By.CLASS_NAME,'btn-search').click()


def incrementDay(browser):
    browser.find_element(By.CLASS_NAME,'btn-icon').click()
    tmp = browser.find_element(By.CLASS_NAME,'day')
    tmp.find_element(By.CLASS_NAME, "increment").click()
    browser.find_element(By.CLASS_NAME,'dtpicker-buttonSet').click()
    browser.find_element(By.CLASS_NAME,'btn-search').click()

    
def getDailyTable(browser,targetData,headings = {'date':[],'time':[],'location':[],'waterLevel':[]}):
    leftTable = browser.find_element(By.CLASS_NAME, "content-view-left").find_element(By.CLASS_NAME, "dataList")
    try:
        locationIDs = [i.get_attribute("id") for i in leftTable.find_elements(By.TAG_NAME, "tr")]
    except Exception as e:
        locationIDs = [i.get_attribute("id") for i in leftTable.find_elements(By.TAG_NAME, "tr")]

    output = pd.DataFrame(headings)
    for locID in locationIDs:
        headings = {'date':[],'time':[],'location':[],'waterLevel':[]}
        leftLocation = leftTable.find_element(By.ID, locID).find_element(By.CLASS_NAME,'first').text
        leftTable.find_element(By.ID, locID).click()

        WebDriverWait(browser, timeout=10).until(ec.text_to_be_present_in_element((By.ID,"stationStr"),leftLocation))

        rightTable = browser.find_element(By.CLASS_NAME, 'content-view-right')
        location = rightTable.find_element(By.ID, 'stationStr').text
        date = browser.find_element(By.ID,'searchtime').get_attribute("value").split()[0]

        print(date,location)

        data = rightTable.find_element(By.TAG_NAME, "tbody").get_attribute('innerHTML')
        soup = BeautifulSoup(data,features="html.parser")
        for row in soup.find_all('tr')[1::]:
            y = row.find_all('span')
            headings['date'].append(y[0].get_text().split()[0])
            headings['time'].append(y[0].get_text().split()[1])
            headings['location'].append(location)
            headings['waterLevel'].append(y[1].get_text())
        output = pd.concat([output,pd.DataFrame(headings)],ignore_index=True)
    output = pd.concat([output,pd.DataFrame(headings)],ignore_index=True)
    return output


def goToMonth(browser,targetDate):
    goToDate(browser,targetDate)

    numberOfDays = calendar.monthrange(targetDate.year,targetDate.month)[1]
    #numberOfDays = 7
    try:
        dataset = pd.DataFrame(headings)
        for i in range(numberOfDays):
            dataset = pd.concat([dataset,getDailyTable(browser,'water-level')],ignore_index=True)
            incrementDay(browser)
    except Exception as e:
        print(e)
        dataset = pd.DataFrame(headings)
        for i in range(numberOfDays):
            dataset = pd.concat([dataset,getDailyTable(browser,'water-level')],ignore_index=True)
            incrementDay(browser)

    tmp_df = dataset.drop_duplicates()
    feather.write_feather(tmp_df,f'{targetDate.year}_{targetDate.month}_pagasa.feather')


if __name__ == "__main__":
    browser = webdriver.Chrome()
    browser.get(pagasa_link+pages[0])
    
    months = []
    month = dt.datetime(2019,7,2)
    #month = dt.datetime(2021,1,2)
    for i in range(100):
        months.append(month)
        month = month + dt.timedelta(calendar.monthrange(month.year,month.month)[1])

    for month in months:
        try:
            goToMonth(browser, month)
        except Exception as e:
            goToMonth(browser, month)

    print("FINISH NA!")


    #print(pd.read_csv(f'{month.year}_{month.month}_pagasa.csv')['location'].value_counts())    

    
    
    
