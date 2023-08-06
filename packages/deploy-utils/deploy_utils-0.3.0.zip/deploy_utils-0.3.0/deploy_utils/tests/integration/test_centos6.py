import os

from deploy_utils import TEMPLATE_DIR
from deploy_utils.fab import CentOS6Fab

from deploy_utils.tests.integration.ec2_base import EC2BaseTestCase


class Centos6TestCase(EC2BaseTestCase):
    
    conf_type = 'test_centos6'
    
    def test_centos6_stuff(self):
        
        centos6_root_fab = CentOS6Fab(self.ec2_conf, self.ec2_instance.public_dns_name, True)
        centos6_root_fab.create_non_root_user()
        
        centos6_fab = CentOS6Fab(self.ec2_conf, self.ec2_instance.public_dns_name)
        centos6_fab.set_timezone('/usr/share/zoneinfo/America/Los_Angeles')
        centos6_fab.update_system()
        centos6_fab.install_helpers()
        centos6_fab.setup_iptables_for_port()
        centos6_fab.install_git()
        centos6_fab.install_jdk()
        centos6_fab.install_maven()
        centos6_fab.install_node()
        
        # pg setup
        init_sql_filename = 'init_test_db.sql'
        init_sql_path = os.path.join(TEMPLATE_DIR, init_sql_filename)
        centos6_fab.install_postgis('test_db', init_sql_path, init_sql_filename)
