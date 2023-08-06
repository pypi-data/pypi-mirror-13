# -*- coding: utf-8 -*-
import logging

from flask import Flask
from flask_restful import Api
from flask_restful_swagger import swagger

from resources.driver_resource import DriverResource
from utils import name_url, extract_params


class libcloud_api(object):
    def __init__(self, config):
        self.config = config
        self.clouds = []
        self.app = Flask(__name__)
        self.api = swagger.docs(Api(self.app), apiVersion='0.1')
        self.resources = {}

    def start(self):
        self.app.run(debug=True)

    def build_controllers(self):
        providers = self.config.providers()
        logging.debug('Loading providers.')
        for provider in providers:
            logging.debug('Adding provider type - %s', provider)
            clouds = self.config.clouds(provider)
            try:
                provider_module = __import__("libcloud.%s.providers" % provider,
                                             fromlist=['libcloud'])
            except ImportError as ime:
                logging.error(ime)

            provider_factory = provider_module.get_driver

            for cloud in clouds:
                logging.debug('Adding driver type - %s.%s', provider, cloud)

                cls = provider_factory(cloud)

                for func in dir(cls):
                    if func[0] != '_':
                        if callable(getattr(cls, func)):
                            address = name_url(provider, cloud, func)
                            if address is not False:
                                params = extract_params(getattr(cls, func))

                                self.api.add_resource(
                                    DriverResource,
                                    address[1],
                                    endpoint='%s_%s_%s' % (
                                        provider,
                                        cloud,
                                        func),
                                    resource_class_args=(
                                        self.config,
                                        cloud,
                                        provider,
                                        cls,
                                        func,
                                        address[0],
                                        params))
                                logging.debug('Added %s - %s',
                                              address[0],
                                              address[1])
