"""
@author: Vojtech Burian
@summary: Selenium Webdriver Python test runner
"""
from shishito.runtime.platform.shishito_execution import ShishitoExecution


class ControlExecution(ShishitoExecution):
    """ ControlExecution for web platform """

    def get_test_result_prefix(self, config_section):
        """ Create string prefix for test results.

        :param str config_section: section in platform/environment.properties config
        :return: str with test result prefix
        """

        # local & browserstack selenium
        try:
            browser = self.shishito_support.get_opt(config_section, 'browser')
            browser_version = self.shishito_support.get_opt(config_section, 'browser_version')

        # saucelabs selenium
        except:
            browser = self.shishito_support.get_opt(config_section, 'browserName')
            browser_version = self.shishito_support.get_opt(config_section, 'version')
        resolution = self.shishito_support.get_opt(config_section, 'resolution')

        return '[%s, %s, %s]' % (browser, browser_version, resolution)
