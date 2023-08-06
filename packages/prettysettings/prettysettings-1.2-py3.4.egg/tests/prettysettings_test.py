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
import json
import unittest
import sys
from os import path, remove, environ
from copy import copy
from datetime import datetime

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from prettysettings import Settings

class SettingsTestBase():

    reference = {
        'intopt': 2, 
        'floatopt':1.1, 
        'boolopttrue': True, 
        'booloptfalse': False, 
        'stropt':'stroptval',
        'intopt_str': 1
    }

    not_default_key = 'not_default_key'

    def test_load_int(self):
        self.assertEqual(self.settings.intopt, self.reference['intopt'],'intopt value does not match')
    def test_load_float(self):
        self.assertEqual(self.settings.floatopt, self.reference['floatopt'],'floatopt value does not match')
    def test_load_bool_true(self):
        self.assertEqual(self.settings.boolopttrue, self.reference['boolopttrue'],'boolopttrue value does not match')
    def test_load_bool_false(self):
        self.assertEqual(self.settings.booloptfalse, self.reference['booloptfalse'],'booloptfalse value does not match')
    def test_load_str(self):
        self.assertEqual(self.settings.stropt, self.reference['stropt'],'stropt value does not match')
    def test_load_int_str(self):
        self.assertEqual(self.settings.intopt_str, self.reference['intopt_str'],'intopt_str value does not match')


    def test_type_int(self):
        self.assertEqual(type(self.settings.intopt), int,'intopt type does not match')
    def test_type_float(self):
        self.assertEqual(type(self.settings.floatopt), float,'floatopt type does not match')
    def test_type_bool_true(self):
        self.assertEqual(type(self.settings.boolopttrue), bool,'boolopttrue type does not match')
    def test_type_bool_false(self):
        self.assertEqual(type(self.settings.booloptfalse), bool,'booloptfalse type does not match')
    def test_type_str(self):
        self.assertEqual(type(self.settings.stropt), str,'intopt type does not match')
    def test_type_int_str(self):
        self.assertEqual(type(self.settings.intopt_str), int,'intopt_str type does not match')

    def test_skip_not_default_key(self):
        self.assertNotIn(self.not_default_key, self.settings.__dict__)



class SettingsTestFromDefaults(unittest.TestCase, SettingsTestBase):

    def setUp(self):

        self.dtformat = '%Y-%m-%d %H:%M:%S'
        self.reference['datetimestr'] = datetime.now().strftime(self.dtformat)


        self.defaults = self.reference

        cshooks = {
            'intopt_times_floatopt': lambda settings: settings.intopt * settings.floatopt,
            'datetime_computed_opt': lambda settings: datetime.strptime(settings.datetimestr, self.dtformat)
        }

        self.settings = Settings(defaults=self.defaults, computed_settings_hooks=cshooks)

    def test_load_computed_intopt_times_floatopt(self):
        self.assertEqual(self.settings.intopt_times_floatopt, self.reference['intopt'] * self.reference['floatopt'],'intopt_times_floatopt value does not match')

    def test_load_computed_datetime(self):
        self.assertEqual(self.settings.datetime_computed_opt, datetime.strptime(self.reference['datetimestr'], self.dtformat),'datetime_computed_opt value does not match')

    def test_exception_save_no_filename(self):
        with self.assertRaises(Exception) as ar:
            self.settings.save()
        self.assertEqual(ar.exception.message, 'No filename given.')


class SettingsTestUpdate(unittest.TestCase, SettingsTestBase):

    def setUp(self):

        self.defaults = {
            'intopt': 11, 
            'floatopt':11.1, 
            'boolopttrue': False, 
            'booloptfalse': False, 
            'stropt':'stroptval_default',
            'intopt_str': 2
        }

        self.settings = Settings(defaults=self.defaults)

        updatecontent = copy(self.reference)
        updatecontent.update({'intopt_str': str(self.reference['intopt_str'])})

        self.settings.update(updatecontent, persist=False)


class SettingsTestSaveLoad(unittest.TestCase, SettingsTestBase):

    def setUp(self):

        self.defaults = {
            'intopt': 11, 
            'floatopt':11.1, 
            'boolopttrue': False, 
            'booloptfalse': False, 
            'stropt':'stroptval_default',
            'intopt_str': 2
        }

        self.filename = './testsettings.json'

        self.settings = Settings(defaults=self.defaults, filename=self.filename)

        updatecontent = copy(self.reference)
        updatecontent.update({'intopt_str': str(self.reference['intopt_str'])})

        self.settings.update(updatecontent) #persist to file

        self.settings = None
        
        #reload from file:
        self.settings = Settings(defaults=self.defaults, filename=self.filename)


    def test_file_exists(self):
        self.assertTrue(path.isfile(self.filename),'file {} not persisted'.format(self.filename))



    def tearDown(self):
        remove(self.filename)



class SettingsTestOverrideFromFile(unittest.TestCase, SettingsTestBase):

    def setUp(self):

        self.defaults = {
            'intopt': 11, 
            'floatopt':11.1, 
            'boolopttrue': False, 
            'booloptfalse': False, 
            'stropt':'stroptval_default',
            'intopt_str': 2
        }

        self.filename = './testsettings.json'
        filecontent = copy(self.reference)
        filecontent.update({'intopt_str': str(self.reference['intopt_str'])})

        filecontent[self.not_default_key] = 'only_file_value'

        with open(self.filename, 'w') as f:
            f.write(json.dumps(filecontent))

        self.settings = Settings(defaults=self.defaults, filename=self.filename)



    def tearDown(self):
        remove(self.filename)


class SettingsTestOverrideFromFileOverrideFromEnv(unittest.TestCase, SettingsTestBase):

    def setUp(self):

        self.defaults = {
            'intopt': 11, 
            'floatopt':11.1, 
            'boolopttrue': False, 
            'booloptfalse': False, 
            'stropt':'stroptval_default',
            'intopt_str': 2
        }

        self.filecontent = {
            'intopt': 111, 
            'floatopt':111.1, 
            'boolopttrue': False, 
            'booloptfalse': False, 
            'stropt':'stroptval_file',
            'intopt_str': 2
        }

        self.filename = './testsettings.json'
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.filecontent))

        environ.update({k: str(self.reference[k]) for k in self.reference.keys()})
        environ[self.not_default_key] = 'only_file_value'


        self.settings = Settings(defaults=self.defaults, filename=self.filename)


    def tearDown(self):
        remove(self.filename)


class SettingsTestOverrideFromFileExceptionStringParsing(unittest.TestCase):

    def setUp(self):

        self.defaults = {
            'intopt_str_err': 13, 
        }

        self.filecontent = {
            'intopt_str_err': 'aa'
        }


        self.filename = './testsettings.json'
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.filecontent))


    def test_exception_parsing_string(self):
        with self.assertRaises(Exception) as ar:
            Settings(defaults=self.defaults, filename=self.filename)



    def tearDown(self):
        remove(self.filename)

