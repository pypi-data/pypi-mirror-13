import os

from deploy_utils import CONFIG_DIR, TEMPLATE_DIR
from deploy_utils.config import ConfigHelper
from deploy_utils.ec2 import launch_new_ec2, tear_down
from deploy_utils.fab import AmazonLinuxFab, CentOS6Fab


def amazon_linux_test_battery():
    
    # create config helper
    ConfHelper = ConfigHelper(CONFIG_DIR, TEMPLATE_DIR) 
        
    # launch ec2
    ec2_conf = ConfHelper.get_config('test_amazon_linux')
    ec2_instance, ec2_connection = launch_new_ec2(ec2_conf, True)
    
    # do fab stuff to ec2 instance
    amzn_linux_fab = AmazonLinuxFab(ec2_conf, ec2_instance.public_dns_name)
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

    # Terminate EC2 instance.
    tear_down(ec2_instance.id, ec2_connection)


def centos6_test_battery():
    
    # create config helper
    ConfHelper = ConfigHelper(CONFIG_DIR, TEMPLATE_DIR) 
        
    # launch ec2
    ec2_conf = ConfHelper.get_config('test_centos6')
    ec2_instance, ec2_connection = launch_new_ec2(ec2_conf, True)
    
    # do fab stuff to ec2 instance
    centos6_fab = CentOS6Fab(ec2_conf, ec2_instance.public_dns_name)
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

    # Terminate EC2 instance.
    tear_down(ec2_instance.id, ec2_connection)