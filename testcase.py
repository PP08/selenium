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
        self.browser.get(url)
        # self.browser.implicitly_wait(10)
        self.responseURLs = []
    def getResponseURL(self):
        # self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.browser.find_element_by_xpath("/html/body").send_keys(Keys.END)
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
                                    setTimeout(function(){console.info(xhr.responseURL)}, 2000);}) \
                                ')
        time.sleep(5)
        logs = self.browser.get_log('browser')
        # print(logs)
        responseURL = []
        indicators = ["laytinmoitronglist", "trang-", "loadListNews", "page-"]
        for el in logs:
            if any(x in el["message"] for x in indicators):
                url = el["message"].split("\"")[1]
                responseURL.append(url)
        return responseURL

    def getResponseURLMultiplePage(self):
        self.browser.implicitly_wait(10)
        self.responseURLs.append(self.getResponseURL())
        self.browser.implicitly_wait(10)
        self.responseURLs.append(self.getResponseURL())
        self.browser.implicitly_wait(10)
        self.responseURLs.append(self.getResponseURL())
        self.browser.quit()
        self.responseURLs = sum(self.responseURLs, [])
        self.responseURLs = {self.url: list(set(self.responseURLs))}

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
            responseURL.getResponseURLMultiplePage()
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
    return data

if __name__ == '__main__':
    data = scheduleThread(8)
    data = sum(data, [])
    data = json.dumps(data)
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
        content = outfile.read().replace('\\', '')
        content = content[1:-2]
        outfile.write(content)
        outfile.close()

