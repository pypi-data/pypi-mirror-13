import os
import time
import shutil
from selenium import webdriver
from selenium_basic_helpers import take_snapshot
from requests_oauthlib import OAuth1


def before_all(context):
    if context.config.userdata.get('test_type') == "selenium":
        if os.path.isfile("snapshots/snapshots_report.html"):
            shutil.rmtree('snapshots/')

def before_feature(context, feature):
    time.sleep(2)

    if context.config.userdata.get('test_type') == "selenium":
        desired_capabilities = {}
        browser_name = context.config.userdata.get('browser_name')
        if browser_name == "firefox":
            desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        elif browser_name == "chrome":
            desired_capabilities = webdriver.DesiredCapabilities.CHROME
        elif browser_name == "ie":
            desired_capabilities = webdriver.DesiredCapabilities.INTERNETEXPLORER
        elif browser_name == "opera":
            desired_capabilities = webdriver.DesiredCapabilities.OPERA
        elif browser_name == "phantomjs":
            desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS
        elif browser_name == "safari":
            desired_capabilities = webdriver.DesiredCapabilities.SAFARI
        elif browser_name == 'local':
            context.browser = webdriver.Firefox()
        if browser_name != 'local':
            desired_capabilities['name'] = str(feature.name + " - Environment: " + context.config.userdata.get('target_env'))
            desired_capabilities['os'] = context.config.userdata.get('operating_system')
            desired_capabilities['os_version'] = context.config.userdata.get('operating_system_version')
            desired_capabilities['browser_version'] = context.config.userdata.get('browser_version')
            desired_capabilities['resolution'] = context.config.userdata.get('screen_resolution')
            desired_capabilities['browserstack.autoWait'] = False
            desired_capabilities['browserstack.debug'] = True
            context.browser = webdriver.Remote(desired_capabilities=desired_capabilities, command_executor=context.config.userdata.get('webdriver_hub'))

    elif context.config.userdata.get('test_type') == "website_status":
        pass

    elif context.config.userdata.get('test_type') == "api":
        pass

    elif context.config.userdata.get('test_type') == "db":
        pass

    if context.config.userdata.get('test_type') == "selenium":
        context.browser.maximize_window()

def before_scenario(context, scenario):
    if context.config.userdata.has_key('wait_between_tests'):
        #print "Waiting " + context.config.wait_between_tests + " seconds before next scenario execution..."
        time.sleep(int(context.config.userdata.get('wait_between_tests')))
        #print "Running test now..."
    if context.config.userdata.get('test_type') == "db":
        pass

def after_scenario(context, scenario):
    pass

def after_step(context, step):
    if context.config.userdata.get('test_type') == "selenium":
        context.browser.title
        if step.status == "failed":
            take_snapshot(context, "base64", "STEP FAILED: " +step.name)

def after_feature(context, feature):
    if context.config.userdata.get('test_type') == "selenium":
        context.browser.quit()

def after_all(context):
    pass