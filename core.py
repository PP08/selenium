from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
desired = DesiredCapabilities.CHROME
desired['loggingPrefs'] = {'browser': 'INFO'}
browser = webdriver.Chrome(desired_capabilities=desired)
browser.get('http://kenh14.vn/star.chn')
browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# browser.find_element_by_xpath("/html/body").send_keys(Keys.END)

# time.sleep(5)
browser.execute_script('function addXMLRequestCallback(callback){ \
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
                            setTimeout(function(){console.info(xhr.response)}, 1000) \
                        }) \
                        ')
time.sleep(5)
logs = browser.get_log('browser')
print(logs)