import requests
import json
import os
import logging


DEFAULT_ELSA = 'http://localhost:8080/'
REG_FILE_NAME = 'registration.json'

DEF_VERSION = 'v1'
DEF_CAP = 1

RETRY = {
    "max": 3,
    "interval": 10
}


class ElsaClient:

    def register(self, elsa_url, path='.'):

        # load from file:
        filepath = os.path.join(path, REG_FILE_NAME)

        print(filepath)

        with open(filepath) as json_file:
            config = json.load(json_file)

        validation = self.__validate(config)

        if validation is False:
            raise ValueError('Invalid registration')

        # POST the registration
        res = requests.post(elsa_url, json=config)

        if res.status_code == 200:
            logging.info('Registered.')

        return res.status_code

    def register_with_defaults(self, elsa_url, service_name, service_location):

        reg = {
            "service": service_name,
            "version": DEF_VERSION,
            "instances": [
                {
                    "location": service_location,
                    "capacity": DEF_CAP
                }
            ]
        }

        res = requests.post(elsa_url, json=reg)
        if res.status_code == 200:
            logging.info('Registered with defaults.')

        return res.status_code

    def __validate(self, reg):
        print(reg)

        # Service name should be provided by user.
        if ('service' in reg) is False:
            raise ValueError('Service name is required.')

        if ('instances' in reg) is False:
            raise ValueError('Instances section is required.')

        instances = reg['instances']

        if len(instances) == 0:
            raise ValueError('You need at least one registration info.')

        if ('version' in reg) is False:
            reg['version'] = DEF_VERSION

        for inst in instances:
            if ('location' in inst) is False:
                raise ValueError('Service location is required.')

            if ('capacity' in inst) is False:
                inst['capacity'] = DEF_CAP

        return True
