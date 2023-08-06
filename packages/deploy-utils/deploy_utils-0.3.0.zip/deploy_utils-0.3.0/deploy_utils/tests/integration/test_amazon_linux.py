import os

from deploy_utils import TEMPLATE_DIR
from deploy_utils.fab import AmazonLinuxFab

from deploy_utils.tests.integration.ec2_base import EC2BaseTestCase


class AmazonLinuxTestCase(EC2BaseTestCase):
    
    conf_type = 'test_amazon_linux'
    
    def test_amazon_linux_stuff(self):
        
        amzn_linux_fab = AmazonLinuxFab(self.ec2_conf, self.ec2_instance.public_dns_name)
        amzn_linux_fab.set_timezone('/usr/share/zoneinfo/America/Los_Angeles')
        amzn_linux_fab.update_system()
        amzn_linux_fab.install_custom_monitoring()
        amzn_linux_fab.install_git()
        amzn_linux_fab.install_jdk()
        amzn_linux_fab.install_maven()
        amzn_linux_fab.install_node()
        
        # pg setup
        init_sql_filename = 'init_test_db.sql'
        init_sql_path = os.path.join(TEMPLATE_DIR, init_sql_filename)
        amzn_linux_fab.install_pg(init_sql_path, init_sql_filename)
