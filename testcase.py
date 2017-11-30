from selenium import webdriver
from selenium.webdriver import ActionChains
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
        # self.chrome_options.add_argument("--headless")
        # self.chrome_options.add_argument('no-sandbox')
        self.browser = webdriver.Chrome(chrome_options=self.chrome_options, desired_capabilities=self.desired)
        self.browser.implicitly_wait(30)
        self.browser.get(url)
        self.responseURLs = []
    def getResponseURL(self):
        self.browser.implicitly_wait(30)
        self.browser.execute_script('$( document ).ajaxSend(function(event, jqxhr, settings) { \
                                  console.info(settings.url) \
                                });')
        # '''change action here'''
        # time.sleep(4)
        # # button = self.browser.find_element_by_class_name('buttonxtttn')
        # print(url)
        try:
        #     # button = self.browser.find_element_by_id(id)
        #     actions1 = ActionChains(self.browser)
        #     actions1.move_to_element_with_offset(url, 0, 0)
        #     actions1.click(url)
        #     actions1.perform()
        #     # self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # # self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            button = self.browser.find_element_by_id('btnViewMore')
            actions1 = ActionChains(self.browser)
            actions1.move_to_element_with_offset(button, 0, 0)
            actions1.click(button)
            actions1.perform()
            # time.sleep(3)
        except:
            pass
    def getResponseURLMultiplePage(self, times):
        for t in range(times):
            self.getResponseURL()
        # logs = self.browser.get_log('browser')
        # responseURL = []
        # indicators = ["laytinmoitronglist", "trang-", "loadListNews", "page-", "page=", "Page", "loadListByPage", "LoadListTinTrongNgay", "pageindex"]
        # for el in logs:
        #     if any(x in el["message"] for x in indicators):
        #         url = self.domain + el["message"].split("\"")[1]
        #         responseURL.append(url)
        #
        # self.responseURLs = {self.url: list(set(responseURL))}
        # time.sleep(5)
        # self.browser.quit()

class Worker(threading.Thread):
    def __init__(self, threadID, listCategory):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.listCategory = listCategory
        self.listResponseURl = []
    def run(self):
        for el in self.listCategory:
            responseURL = ResponseURL(el)
            print(el)
            # menu = responseURL.browser.find_element_by_class_name('video-menu')
            # links = menu.find_elements_by_xpath('.//ul/li')
            # for t in links:
            #     # button = responseURL.browser.find_element_by_id(t)
            #     # button.click()
            #     # button = temp.find_element_by_xpath(".//a")
            #     # print(button.text)
            #     actions = ActionChains(responseURL.browser)
            #     actions.move_to_element_with_offset(t, 0, 0)
            #     actions.click(t)
            #     actions.perform()
            #     responseURL.browser.implicitly_wait(6)
            #     time.sleep(6)
            #
            #     # list_url = ["aCategory_1", "aCategory_2", "aCategory_3", "aCategory_4"]
            #     list_url = []
            #     for i in range(1, 5):
            #         xpath = '//*[@id="video-paging"]/a[{}]'.format(i)
            #         list_url.append(responseURL.browser.find_element_by_xpath(xpath))
            responseURL.getResponseURLMultiplePage(4)
                # print(responseURL.responseURLs)
                # responseURL.responseURLs = []
                # self.listResponseURl.append(responseURL.responseURLs)
        logs = responseURL.browser.get_log('browser')
        test = []
        indicators = ["laytinmoitronglist", "trang-", "loadListNews", "page-", "page=", "Page", "loadListByPage",
                      "LoadListTinTrongNgay", "pageindex", "GetNewestVideoByZone", "video/latest/"]
        for el in logs:
            if any(x in el["message"] for x in indicators):
                # url = responseURL.domain + el["message"].split("\"")[1]
                test.append(el["message"])
        print(list(set(test)))
            # self.responseURLs = {self.url: list(set(responseURL))}
def getCategory(file_path):
    file = open(file_path, 'r')
    content = file.readlines()
    content = [line.replace('\n', '') for line in content]
    return content

def scheduleThread(numThreads):
    category = getCategory('nld.txt')
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
    data = scheduleThread(1)
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