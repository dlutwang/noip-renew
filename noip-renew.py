#!/usr/bin/python
# Copyright 2017 loblab
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from selenium import webdriver
import time
import sys
 
class Robot:

    LOGIN_URL = "https://www.noip.com/login"
    HOST_URL = "https://my.noip.com/#!/dynamic-dns"
    NUM_HOSTS = 3

    def __init__(self, debug=0):
        self.debug = debug
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        # To run Chrome as root, use 'no-sandbox' option, but it is not safe
        #options.add_argument("no-sandbox")
        options.add_argument("window-size=1200x800")
        self.browser = webdriver.Chrome(chrome_options=options)
        self.browser.set_page_load_timeout(30)

    def log_msg(self, msg, level=None):
        tstr = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        if level is None:
            level = self.debug
        if level > 0:
            print("%s - %s" % (tstr, msg))

    def login(self, username, password):
        self.log_msg("Open %s..." % Robot.LOGIN_URL)
        self.browser.get(Robot.LOGIN_URL)
        if self.debug > 1:
            self.browser.save_screenshot("debug1.png")
 
        self.log_msg("Login...")
        ele_usr = self.browser.find_element_by_name("username")
        ele_pwd = self.browser.find_element_by_name("password")
        ele_usr.send_keys(username)
        ele_pwd.send_keys(password)
        #self.browser.find_element_by_name("login").click()
        form = self.browser.find_element_by_id("clogs")
        form.submit()
        if self.debug > 1:
            time.sleep(1)
            self.browser.save_screenshot("debug2.png")

    @staticmethod
    def xpath_of_button(cls_name):
        return "//button[contains(@class, '%s')]" % cls_name 

    def update_hosts(self):
        self.log_msg("Open %s..." % Robot.HOST_URL)
        self.browser.get(Robot.HOST_URL)
        invalid = True
        retry = 5
        while retry > 0:
            time.sleep(1)
            buttons_todo = self.browser.find_elements_by_xpath(Robot.xpath_of_button('btn-confirm'))
            buttons_done = self.browser.find_elements_by_xpath(Robot.xpath_of_button('btn-manage'))
            count = len(buttons_todo)
            if count + len(buttons_done) == Robot.NUM_HOSTS:
                invalid = False
                break
            retry -= 1
        if invalid:
            self.log_msg("Invalid page or something wrong. See error.png", 2)
            self.browser.save_screenshot("error.png")
            return False
        if self.debug > 1:
            self.browser.save_screenshot("debug3.png")
        self.log_msg("Hosts to be confirmed: %d" % count)
        for button in buttons_todo:
            button.click()
            time.sleep(1)
        self.browser.save_screenshot("result.png")
        self.log_msg("Confirmed hosts: %d" % count, 2)
        return True

    def run(self, username, password):
        rc = 0
        try:
            self.login(username, password)
            if not self.update_hosts():
                rc = 3
        except Exception as e:
            self.log_msg(str(e), 2)
            rc = 2
        finally:
            self.browser.quit()
        return rc

def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) < 3:
        print("Usage: %s <username> <password> [<debug-level>]" % argv[0])
        return 1

    username = argv[1]
    password = argv[2]
    debug = 1
    if len(argv) > 3:
        debug = int(argv[3])

    robot = Robot(debug)
    return robot.run(username, password)

if __name__ == "__main__":
    sys.exit(main())
