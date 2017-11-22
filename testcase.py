from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from selenium.webdriver.chrome.options import Options
import threading
import json
import re

class ResponseURL():
    def __init__(self, url):
        self.url = url
        self.domain = re.search(r'(http|https):\/\/(.*?)/', url).group(0)[:-1]
        self.desired = DesiredCapabilities.CHROME
        self.desired['loggingPrefs'] = {'browser': 'ALL'}
        self.chrome_options = Options()
        self.prefs = {"profile.managed_default_content_settings.images": 2}
        self.chrome_options.add_experimental_option("prefs", self.prefs)
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('no-sandbox')
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options, desired_capabilities=self.desired)
        self.browser.implicitly_wait(30)
        self.browser.get(url)
        self.responseURLs = []
    def getResponseURL(self):
        self.browser.implicitly_wait(30)
        self.browser.execute_script('$( document ).ajaxSend(function(event, jqxhr, settings) { \
                                  console.info(settings.url) \
                                });')
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(6)
    def getResponseURLMultiplePage(self, times):
        for t in range(times):
            self.getResponseURL()
        logs = self.browser.get_log('browser')
        responseURL = []
        indicators = ["laytinmoitronglist", "trang-", "loadListNews", "page-", "page=", "Page"]
        for el in logs:
            if any(x in el["message"] for x in indicators):
                url = self.domain + el["message"].split("\"")[1]
                responseURL.append(url)

        self.responseURLs = {self.url: list(set(responseURL))}
        # time.sleep(5)
        self.browser.quit()

class Worker(threading.Thread):
    def __init__(self, threadID, listCategory):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.listCategory = listCategory
        self.listResponseURl = []
    def run(self):
        for el in self.listCategory:
            print(el)
            responseURL = ResponseURL(el)
            responseURL.getResponseURLMultiplePage(3)
            self.listResponseURl.append(responseURL.responseURLs)

def getCategory(file_path):
    file = open(file_path, 'r')
    content = file.readlines()
    content = [line.replace('\n', '') for line in content]
    return content

def scheduleThread(numThreads):
    category = getCategory('category.txt')
    numElements = len(category) // numThreads
    listThreads = []
    data = []
    for i in range(numThreads - 1):
        temp = category[i * numElements:(i + 1) * numElements]
        listThreads.append(Worker(i, temp))
    temp = category[(numThreads - 1) * numElements:]
    listThreads.append(Worker(numThreads - 1, temp))

    for thread in listThreads:
        thread.start()
    for thread in listThreads:
        thread.join()
    for thread in listThreads:
        data.append(thread.listResponseURl)
    print("*here*")
    return data

if __name__ == '__main__':
    data = scheduleThread(8)
    data = sum(data, [])
    data = json.dumps(data)
    with open('temp.json', 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()
    temp = open('temp.json', 'r').read()
    with open('data.json', 'w') as outfile:
        content = temp.replace('\\', '')
        content = content[1:-1]
        outfile.write(content)
        outfile.close()