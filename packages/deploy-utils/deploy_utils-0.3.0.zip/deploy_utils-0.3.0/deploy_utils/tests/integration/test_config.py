import ConfigParser
import os

from unittest import TestCase

import deploy_utils
from deploy_utils import CONFIG_DIR, TEMPLATE_DIR
from deploy_utils.config import DefaultConfig, ConfigHelper


class TestDefaultConfig(TestCase):

    def setUp(self):
        cp = ConfigParser.ConfigParser()
        cp.set('DEFAULT', 'test_key', 'test_value')
        self.default_conf = DefaultConfig(cp)

    def test_get(self):
        assert 'test_value' == self.default_conf.get('test_key')

    def test_make_params_for_template(self):
        out = self.default_conf.make_params_for_template(os.path.join(TEMPLATE_DIR, 'test_conf.ini'))
        assert 'test_key' in out
        assert out['test_key'] == 'test_value'
        assert 'chicharrones' in out
        assert out['chicharrones'] == None


class TestConfigHelper(TestCase):

    def setUp(self):
        self.conf_helper = ConfigHelper(CONFIG_DIR, TEMPLATE_DIR)
        self.conf_file = os.path.join(CONFIG_DIR, 'test_conf_helper.ini')
        try:
            os.remove(self.conf_file)
        except:
            pass

    def tearDown(self):

        for file_to_remove in [self.conf_file,
                               os.path.join(CONFIG_DIR, 'test_conf_helper_out.ini')]:
            try:
                os.remove(file_to_remove)
            except:
                pass

    def test_get_config(self):

        with open(self.conf_file, 'w') as f:
            f.write("[DEFAULT]\ntest_key = {test_val}")

        conf = self.conf_helper.get_config('test_conf_helper')
        assert isinstance(conf, DefaultConfig)
        assert '{test_val}' == conf.get('test_key')

    def test_setup(self):

        deploy_utils.config.input = lambda _: 'blah'
        self.conf_helper.setup('test_conf_helper')

        assert os.path.exists(self.conf_file)
        with open(self.conf_file) as f:
            contents = f.read()
            assert 'test_key = blah' in contents

    def test_write_template(self):

        for outfilename in [None, 'test_conf_helper_out.ini']:
            self.conf_helper.write_template(dict(test_key='blah blah'),
                                            'test_conf_helper.ini',
                                            outfilename)

            if outfilename is None:
                outfilename = 'test_conf_helper.ini'

            outpath = os.path.join(CONFIG_DIR, outfilename)

            assert os.path.exists(outpath)
            with open(outpath) as f:
                contents = f.read()
                assert 'test_key = blah blah' in contents
