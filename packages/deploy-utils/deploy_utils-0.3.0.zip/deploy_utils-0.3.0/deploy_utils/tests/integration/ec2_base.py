from unittest import TestCase

from deploy_utils import CONFIG_DIR, TEMPLATE_DIR
from deploy_utils.config import ConfigHelper
from deploy_utils.ec2 import launch_new_ec2, tear_down


class EC2BaseTestCase(TestCase):
    
    conf_type = None
    
    def setUp(self):
        '''Create a new EC2 instance.'''
        
        if not self.conf_type:
            raise Exception('Conf Path Must Be Set')
        
        ConfHelper = ConfigHelper(CONFIG_DIR, TEMPLATE_DIR) 
        
        self.ec2_conf = ConfHelper.get_config(self.conf_type)
        ec2_instance, ec2_connection = launch_new_ec2(self.ec2_conf, True)
        self.ec2_instance = ec2_instance
        self.ec2_connection = ec2_connection

    def tearDown(self):
        '''Terminate EC2 instance.'''
        tear_down(self.ec2_instance.id, self.ec2_connection)
