# Implements CloudAtCost Panel setting configuration
# Last Working State: 2015-11-20
# Author: makefu github@syntax-fehler.de

import requests
from bs4 import BeautifulSoup
import logging
log = logging.getLogger("CACPanel")

# currently cac only supports ipv4
GET_IP_URL = "http://ipv4.icanhazip.com"

BASE_URL = "https://panel.cloudatcost.com"
START_URL = BASE_URL + "/login.php"
LOGIN_URL = BASE_URL + "/manage-check2.php"
REFER_URL = BASE_URL + "/index.php"
SETTINGS_URL = BASE_URL + "/panel/_config/userSettings.php"
GEN_API_URL = BASE_URL + "/panel/_config/APIfunc.php"

refer_header = { 'Referer' : REFER_URL }

def errortext(code):
    try:
        code = int(code)
        if code == 2:
            return "Wrong username or password"
        elif code == 21:
            return "2 Factor Authentication : IP Denied." + \
                   "Please Check your email for instruction."
        else:
            raise Exception()
    except:
        pass
    return "Unknown errorcode {}".format(code)


class CACPanel:
    """Base class for making requests to the cloud at cost Panel
    """
    useragent = "Mozilla/5.0"
    def __init__(self, email, password):
        """Return a CACPanel object.

        Required Arguments:
        email - The email address used to authenticate to the API.
        password - your panel password
        """
        self.email = email
        self.password = password
        self.s = None
        # Do not know about this one yet
        self.login()

    def _init_session(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": self.useragent})
        # grab cookies
        self.s.get(START_URL)

    def login(self):
        self._init_session()
        login_data = { "username": self.email,
                       "password": self.password,
                       "failedpage": "login-failed.php",
                       "submit": "Login"}
        ret = self.s.post(LOGIN_URL, data=login_data)

        if "/login.php?error" in ret.url:
            errorcode = ret.url.split('error=')[-1]
            etext = "Login Failed - Reason: {}".format(errortext(errorcode))
            log.error(etext)
            raise Exception (etext)

    def get_settings(self):
        """ Screenscrapes User Settings """
        ret = self.s.get(SETTINGS_URL, headers=refer_header)
        soup = BeautifulSoup(ret.text,'html.parser')
        ret = { i:soup.find(id=i)['value']
                for i in ['city', 'country', 'state',
                          'apiip', 'phone', 'email',
                          'company', 'zip', 'address1' ] }
        ret['apicode'] = soup.find(id='APIgen').get_text().split()[0]
        return ret

    def gen_apicode(self):
        ret = self.s.get(GEN_API_URL, headers=refer_header)
        return self.get_settings()['apicode']

    def set_apiip_to_ext(self):
        """ convenience function which sets the api ip address to whatever is
        your current external ip.
        """
        ip = self.s.get(GET_IP_URL).text.strip()
        # TODO test if ipv4 returned
        return self.set_apiip(ip)

    def add_apiip_to_ext(self):
        ip = self.s.get(GET_IP_URL).text.strip()
        # TODO test if ipv4 returned
        return self.add_apiip(ip)

    def set_apiip(self, ip):
        return self.set_settings({"APIIP": ip } )['APIIP']

    def add_apiip(self, ip):
        new_ips = ",".join(filter(None,
            set(self.get_settings()['apiip'].split(',') + [ ip ])))
        return self.set_settings({"APIIP": new_ips } )['APIIP']

    def set_settings(self, dic):
        """
        override the current settings with the dic
        """
        cur = self.get_settings()
        default_params = {
                "UP": 1,
                "PS": "********",
                "LA": "no", #TODO: find out what it does
                "CS": ""}   #TODO: find out what this does
        mapping = {
                "EM": cur['email'],
                "CM": cur['company'],
                "AD": cur['address1'],
                "PH": cur['phone'],
                "CY": cur['city'],
                "ST": cur['state'],
                "ZP": cur['zip'],
                "CN": cur['country'],
                "APIIP":cur['apiip']}

        mapping.update(default_params)
        mapping.update(dic)

        # TODO: Error handling
        ret = self.s.get(SETTINGS_URL,
                         params=mapping,
                         headers=refer_header)
        return mapping

