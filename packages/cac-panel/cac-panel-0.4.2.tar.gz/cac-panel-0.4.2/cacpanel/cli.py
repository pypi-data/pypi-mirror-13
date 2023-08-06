#!/usr/bin/env python
""" usage:
        cac-panel [options] (settings|new-apicode)
        cac-panel [options] (set-api-ip|add-api-ip) [IPADDR]

Options:
    --config PATH           Set configuration path
    --lol LOGLEVEL          Sets the log level [Default: WARN]


the config is in json format and may contain the following variables:
    {
        "email":"",
        "password":"",
        "apicode":""
    }

Panel functionality requires 'email' and 'password' variables

For full functionality password is required, apicode can be queried if
necessary.
Configuration can also be set as CAC_CONFIG environment variable. If no
configuration is provided, cac-cli will look in ~/.config/cac/config.json
"""
import sys,os,json
from docopt import docopt
from cacpanel import CACPanel
from os.path import expanduser
import logging

log = logging.getLogger('cac-panel')

def set_lol_from_string(lol):
    numeric_level = getattr(logging,lol.upper(),None)
    if not isinstance(numeric_level,int):
        raise AttributeError('No such log level {}'.format(lol))
    logging.basicConfig(level=numeric_level)
    log.setLevel(numeric_level)
    log.debug("Log Level {}".format(lol))

def json_out(obj):
    print(json.dumps(obj,indent=2))

def handle_panel(cfg,args):
    mail, passwd = (cfg.get('email',None),cfg.get('password',None))
    if not (mail and passwd):
        log.error("Panel Requires Username and Password in configuration")
        sys.exit(1)
    log.debug("{} {}".format(mail,passwd))
    p = CACPanel(mail,passwd)
    if args['settings']:
        json_out(p.get_settings())
    elif args['new-apicode']:
        log.info("Generating new apicode")
        print(p.gen_apicode())
    elif args['set-api-ip']:
        ip = args['IPADDR']
        if ip is not None:
            log.info('setting API IP Address to {}'.format(ip))
            p.set_apiip(ip)
            print(ip)
        else:
            log.info('using current external ip as new api-ip')
            ret = p.set_apiip_to_ext()
            log.info('new api ip: {}'.format(ret))
            print(ret)
    elif args['add-api-ip']:
        ip = args['IPADDR']
        if ip is not None:
            log.info('updating API IP Address to {}'.format(ip))
            p.add_apiip(ip)
            print(ip)
        else:
            log.info('using current external ip as additional api-ip')
            ret = p.add_apiip_to_ext()
            log.info('new api ip: {}'.format(ret))
            print(ret)

def handle_api(cfg,args):
    raise NotImplementedError()

def main():
    args = docopt(__doc__)
    set_lol_from_string(args['--lol'])

    cfgfile = args['--config'] or \
            os.environ.get('CAC_CONFIG',
                expanduser('~/.config/cac/config.json'))

    log.info('using configuration path "{}"'.format(cfgfile))
    with open(cfgfile) as f:
        cfg = json.load(f)

    handle_panel(cfg,args)


if __name__ == '__main__':
    main()

