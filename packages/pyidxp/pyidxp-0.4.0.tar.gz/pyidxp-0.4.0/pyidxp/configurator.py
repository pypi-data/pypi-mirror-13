from consul import Consul, ConsulException
from json import load as jsonload, loads as jsonloads
from shutil import which
from os.path import isfile


def configuration(key, config_file='config.json'):
    if consul_present():
        c = Consul()
        try:
            value = c.kv.get(key)[1]['Value'].decode()
            config = jsonloads(value)
            return config
        except ConsulException:
            print("==> Configurator: Couldn't get configuration from Consul, "
                  "reading from file")
    return jsonload(open(config_file, 'r'))


def consul_present():
    if which('consul'):
        return True
    if isfile('/opt/consul/bin/consul'):
        return True
    return False
