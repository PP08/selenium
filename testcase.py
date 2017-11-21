from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options
import threading
import json
def getCategory(file_path):
    file = open(file_path, 'r')
    content = file.readlines()
    content = [line.replace('\n', '') for line in content]
    return content

class ResponseURL():
    def __init__(self, url):
        self.url = url
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
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # self.browser.find_element_by_xpath("/html/body").send_keys(Keys.END)
        self.browser.execute_script('function addXMLRequestCallback(callback){ \
                                    var oldSend, i; \
                                    if( XMLHttpRequest.callbacks ) { \
                                        XMLHttpRequest.callbacks.push( callback ); \
                                    } else { \
                                        XMLHttpRequest.callbacks = [callback]; \
                                        oldSend = XMLHttpRequest.prototype.send; \
                                        XMLHttpRequest.prototype.send = function(){ \
                                            for( i = 0; i < XMLHttpRequest.callbacks.length; i++ ){ \
                                                XMLHttpRequest.callbacks[i]( this ); \
                                            } \
                                            oldSend.apply(this, arguments); \
                                        } \
                                    } \
                                } \
                                addXMLRequestCallback(function (xhr){ \
                                    setTimeout(function(){console.info(xhr.responseURL)}, 10000);}) \
                                ')
        # self.browser.implicitly_wait(30)
        time.sleep(10)
    def getResponseURLMultiplePage(self, times):
        for t in range(times):
            self.getResponseURL()
        logs = self.browser.get_log('browser')
        responseURL = []
        indicators = ["laytinmoitronglist", "trang-", "loadListNews", "page-"]
        for el in logs:
            if any(x in el["message"] for x in indicators):
                url = el["message"].split("\"")[1]
                responseURL.append(url)

        self.responseURLs = {self.url: list(set(responseURL))}
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