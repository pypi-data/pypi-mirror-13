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
from distutils.util import strtobool

class Settings:

    def _parse_to_default_type(self, defaultkey, parsevalue):
        if type(self.defaults[defaultkey]) == bool and type(parsevalue) != bool:
            return bool(strtobool(parsevalue))
        else:
            return type(self.defaults[defaultkey])(parsevalue)

    def _parse_filter(self, settings):
        return {k: self._parse_to_default_type(k, settings[k]) for k in settings.keys() if k in self.defaults.keys()}

    def __init__(self, defaults, filename = None, computed_settings_hooks = None): 

        self.defaults = defaults

        self.filename = filename

        #set defaults
        self.__dict__.update(self.defaults)

        #override from settings.json file
        if self.filename:
            if os.path.isfile(self.filename):
                with open(self.filename, 'r') as f:
                    settings = json.loads(f.read())
                    self.__dict__.update(self._parse_filter(settings))

        #override from env variables:
        self.__dict__.update(self._parse_filter(os.environ))

        if computed_settings_hooks:
            for k in computed_settings_hooks.keys():
                self.__dict__.update({k: computed_settings_hooks[k](self)})


    def __str__(self):
        return json.dumps({k: self.__dict__[k] for k in self.defaults.keys()},
                sort_keys=True, indent=4, separators=(',', ': '))

    def update(self, settings, persist=True):
        self.__dict__.update(self._parse_filter(settings))
        if persist:
            self.save()

    def save(self):
        if self.filename:
            with open(self.filename, 'w') as f:
                f.write(str(self))
        else:
            raise Exception('No filename given.')
            