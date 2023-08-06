from __future__ import absolute_import

import time

from appium import webdriver

from shishito.runtime.environment.shishito import ShishitoEnvironment


class ControlEnvironment(ShishitoEnvironment):
    """ SauceLabs Selenium control environment. """

    def call_browser(self, config_section):
        """ Start webdriver for given config section. Prepare capabilities for the webdriver. If saucelabs setting has value,
        webdriver will be connected to saucelabs. Otherwise appium_url setting will be used.

        :param str config_section: section in platform/environment.properties config
        :return: created webdriver
        """

        # get browser capabilities
        capabilities = self.get_capabilities(config_section)

        saucelabs_credentials = self.shishito_support.get_opt('saucelabs')
        remote_url = 'http://%s@ondemand.saucelabs.com:80/wd/hub' % saucelabs_credentials

        # get driver
        return self.start_driver(capabilities, remote_url)

    def get_capabilities(self, config_section):
        """ Return dictionary of capabilities for specific config combination.

        :param str config_section: section in platform/environment.properties config
        :return: dict with capabilities
        """

        get_opt = self.shishito_support.get_opt
        return {
            'platform': get_opt(config_section, 'platform'),
            'browserName': get_opt(config_section, 'browserName'),
            'version': get_opt(config_section, 'version'),
            'name': self.get_test_name() + time.strftime('_%Y-%m-%d'),
        }

    def get_pytest_arguments(self, config_section):
        """ Get environment specific arguments for pytest.

        :param config_section: section in platform/environment.properties config
        :return: dict with arguments for pytest or None
        """

        pytest_args = {
            '--platform': '--platform=%s' % self.shishito_support.get_opt(config_section, 'platform'),
            '--browserName': '--browserName=%s' % self.shishito_support.get_opt(config_section, 'browserName'),
            '--browser_version': '--browser_version=%s' % self.shishito_support.get_opt(config_section, 'version')
        }

        saucelabs_credentials = self.shishito_support.get_opt('saucelabs')
        if saucelabs_credentials:
            pytest_args['--saucelabs'] = '--saucelabs=%s' % saucelabs_credentials

        return pytest_args

    def start_driver(self, capabilities, remote_driver_url):
        """ Prepare selenium webdriver.

        :param capabilities: capabilities used for webdriver initialization
        :param remote_driver_url: url to which the driver will be connected
        """

        driver = webdriver.Remote(
            command_executor=remote_driver_url,
            desired_capabilities=capabilities,
        )

        return driver
