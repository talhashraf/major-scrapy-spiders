import re

from scrapy import Spider
from scrapy.http import Request, FormRequest


class FacebookLogin(Spider):
    download_delay = 0.5

    usr = "" # username/email/phone number
    pwd = "" # password

    def start_requests(self):
        return [Request("https://m.facebook.com/", callback=self.parse)]

    def parse(self, response):
        return FormRequest.from_response(response,
                                            formdata={
                                                'email': self.usr,
                                                'pass': self.pwd
                                            }, callback=self.remember_browser)

    def remember_browser(self, response):
        if re.search(r'(checkpoint)', response.url):
            # Use 'save_device' instead of 'dont_save' to save device
            return FormRequest.from_response(response,
                                                formdata={'name_action_selected': 'dont_save'},
                                                callback=self.after_login)

    def after_login(self, response):
        pass
