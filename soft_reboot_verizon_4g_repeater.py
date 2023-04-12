#!/usr/bin/python3
"""Selenium script for Python will do a soft/safe reboot on a
   Verizon 4G LTE Network Extender (ASK-SFE116)"""
# Tim H 2023
#   This Selenium script for Python will do a soft/safe reboot on a
#   Verizon 4G LTE Network Extender. My network extender has issues after
#   being powered on for over a week or so, and there is no way in the GUI
#   to schedule or automate reboots. This script logs into the web interface
#   and simulates clicking the soft reboot button.
#   Takes about 3-4 minutes to finish rebooting and restarting all services.
#   SKU: ASK-SFE116
#   FCC ID: H8N-ASK-SFE116
#
#   Developed in the following environment, known to be working:
#       * Verizon Network Extender software version: GA5.11 - V0.5.011.1322
#       * macOS 13.3 (Ventura)
#       * Python 3.9.6
#       * Selenium 4.8.3
#
# References:
#   https://www.geeksforgeeks.org/driving-headless-chrome-with-python/
#   https://www.thepythoncode.com/article/automate-login-to-websites-using-selenium-in-python
#   https://www.verizon.com/support/lte-network-extender/
#   https://www.lambdatest.com/blog/handling-errors-and-exceptions-in-selenium-python/

import sys
import os
import getopt
from time import sleep
import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def running_inside_container():
    """Returns boolean of whether inside Docker container or not"""
    return os.getenv('RUNNING_IN_DOCKER_CONTAINER', False)


def main(argv):
    """Main"""
    # assume real run, not dry run

    # DEBUG: Log the current time, verify cron is running
    print("[", datetime.datetime.now(), "] Starting soft_reboot_verizon_4g_repeater.py...")

    dry_run = False

    usage = ('soft_reboot_verizon_4g_repeater.py --url=<url> '
             '--password-file=<filename> '
             '[--dry-run]')

    try:
        # extract the command line arguments
        opts, args = getopt.getopt(argv, "hi:o:",
                                   ["url=", "password-file=", "dry-run"])
    except getopt.GetoptError:
        print("Error in parameters." + usage)
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("--url"):
            # HTTPS URL for the Verizon LTE Extender management page
            # it's just regular HTTPS over TCP 443
            url_to_render = arg
        elif opt in ("--password-file"):
            # path to text file that has the password on a single line
            # this is the password used to login. There is no username
            # the factory password is printed on a label on the Verizon device.
            password_file = arg
        elif opt in ("--dry-run"):
            dry_run = True

    # load password from file
    try:
        with open(password_file, 'r') as file:
            password_to_use = file.read().rstrip()
    except IOError:
        print("password-file=", password_file, "and Current Path is: ", os.getcwd())
        sys.exit(
            "Error: Password file does not exist or user does not have read permissions on it")

    options = Options()
    # set the new instance of Chrome to be headless, no-GUI
    options.add_argument("--headless=new")

    # ignore SSL certificate errors, since the Verizon device uses a
    # self signed certificate
    options.add_argument("--ignore-certificate-errors")

    # set the window size to a reasonable size for screenshots and
    # rendering the modals.
    options.add_argument("--window-size=1920,1200")

    if running_inside_container():
        # TODO: investigate problems or security flaws it can introduce
        # the --no-sandbox seems to be required for Docker deployments
        options.add_argument("--no-sandbox")

        # not sure about the others:
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")

    # create the Chrome instance
    driver = webdriver.Chrome(options=options)

    # have the headless Chrome fetch the specific URL
    driver.get(url_to_render)

    # TODO: add check to verify that URL was successfully fetched

    # wait for it to finish loading. I know there's are more elegant ways
    # to poll/wait for the site to finish loading, but I don't really care
    # for this simple use case. It's just a very simple LAN site.
    sleep(5)

    # find and fill in the password field
    password_element = driver.find_element(By.ID, 'password')
    password_element.send_keys(password_to_use)

    # click the submit button
    login_button = driver.find_element(By.ID, 'btn_login')

    # intentionally separating it out for debugging ease
    # https://www.geeksforgeeks.org/click-element-method-selenium-python/
    # https://stackoverflow.com/questions/68780249/how-to-get-a-response-with-selenium-when-a-click-is-sent-to-server-true-or-fa
    login_response = login_button.click()

    # wait for it to finish loading
    sleep(3)

    try:
        # checking to see if the Sign Out button/graphic exists
        # if so, then login was successful
        driver.find_element(By.ID, 'btn_sign')
        print('Successfully found the logout button, so login must have been successful')
    except NoSuchElementException:
        # found an element that means the password was wrong. Submit worked
        # but auth failed.
        if driver.find_element(By.ID, 'signinLayer_error'):
            driver.quit()
            sys.exit("Incorrect password. Exiting.")
        else:
            # unknown error
            # login failed, exit program and display a message
            driver.quit()
            sys.exit("Login failed, unable to find the logout button. Exiting")

    # navigate to the page with the soft reboot button
    driver.get(url_to_render + '/#settings/reset')
    # wait for it to finish loading
    sleep(3)

    # find and click the first (warning) button to restart
    # this causes a modal to pop-up in the existing URL that warns the user
    # and confirms that they want to reboot.
    driver.find_element(By.ID, 'btn_complete_restart').click()

    # wait for the modal to load
    sleep(5)

    # find the final reboot button but don't click it yet.
    # this one has a NAME but not an ID.
    reboot_button_confirm = driver.find_element(By.NAME, 'box_ok')
    # print ("found the final reboot button")

    # do any debugging here, used to take screenshots for debugging.
    # screenshot_output_file='screenshot.png'
    # driver.save_screenshot(screenshot_output_file)
    # driver.get_screenshot_as_png()

    # click the final reboot button
    if dry_run:
        print("Found the final reboot button but aborting since this is a dry run.")
    else:
        reboot_button_confirm.click()
        print("Rebooting the repeater now...")
        # for some reason, you do have to wait a moment before exiting the browser
        sleep(5)

    # properly clean up the Chrome instance
    driver.quit()


if __name__ == "__main__":
    main(sys.argv[1:])
    print("[", datetime.datetime.now(), "] soft_reboot_verizon_4g_repeater.py Python script finished successfully.")
