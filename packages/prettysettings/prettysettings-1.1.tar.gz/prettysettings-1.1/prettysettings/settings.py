"""

Copyright 2015 Stefano Terna

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
import json
import logging

class Settings:

    def __init__(self, defaults, filename): 

        self.defaults = defaults

        self.filename = filename
        #set defaults
        self.__dict__.update(self.defaults)

        #override from settings.json file
        try:
            with open(self.filename, 'r') as f:
                settings = json.loads(f.read())
                self.__dict__.update(settings)
        except Exception as e:
            logging.error(e)

        #override from env variables:
        self.__dict__.update({k: type(self.defaults[k])(os.environ[k]) for k in os.environ.keys() if k in self.defaults.keys()})

        logging.info(str(self))

    def __str__(self):
        return json.dumps({k: self.__dict__[k] for k in self.defaults.keys()},
                sort_keys=True, indent=4, separators=(',', ': '))

    def update(self, settings):
        self.__dict__.update({k: settings[k] for k in settings.keys() if k in self.defaults.keys()})
        self.save()
        logging.info("updated")
        logging.info(str(self))        

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                f.write(str(self))
        except Exception as e:
            logging.info(e)
            