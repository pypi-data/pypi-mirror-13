import sys
import time

from fabric.api import env, run, sudo, cd, put
from fabric.contrib.files import exists
from fabric.exceptions import NetworkError
from fab_deploy.crontab import crontab_update

from deploy_utils import CONFIG_DIR, TEMPLATE_DIR
from deploy_utils.config import ConfigHelper


class Fab:
    
    def __init__(self, conf, host_name, root_user=False, fab_log_filename='fab.log'):
        '''Constructor for Class.  Sets up fabric environment.
        
        Args:
            conf (deploy_utils.config.DefaultConfig): Configuration vals for machine
            host_name (string): host name
            root_user (boolean, default=False): whether to login as root user
            fab_log_filename (string, default='fab.log'): name of log file for saving of fab logs
        '''
        
        self.conf = conf
        self._config_helper = ConfigHelper(CONFIG_DIR, TEMPLATE_DIR)
        
        if root_user:
            self.user = 'root'
            self.user_home = '/root'
        else:
            try:
                env.password = conf.get('non_root_password')
            except:
                pass
            self.user = conf.get('non_root_user')
            self.user_home = unix_path_join('/home', self.user)
        
        self.config_dir = unix_path_join(self.user_home, 'conf')
        self.script_dir = unix_path_join(self.user_home, 'scripts')
        self.data_dir = unix_path_join(self.user_home, 'data')
        
        env.host_string = '{0}@{1}'.format(self.user, host_name)
        env.key_filename = [conf.get('key_filename')]
        sys.stdout = FabLogger(fab_log_filename)
        
        max_retries = 6
        num_retries = 0
        ssh_sleep = 10
        
        retry = True
        while retry:
            try:
                # SSH into the box here.
                run('uname')
                retry = False
            except NetworkError as e:
                print(e)
                if num_retries > max_retries:
                    raise Exception('Maximum Number of SSH Retries Hit.  Did instance get configured with ssh correctly?')
                num_retries += 1 
                print('SSH failed (the system may still be starting up), waiting {0} seconds...'.format(ssh_sleep))
                time.sleep(ssh_sleep)
                
                
class RHELFab(Fab):
    '''Red Hat Enterpise Linux -ish Fab class.
    Has various commands that only work with RHEL-like distros.
    '''
            
    def install_git(self):
        '''Installs git.
        '''
        
        sudo('yum -y install git')
        
    def install_jdk(self):
        '''Installs jdk devel, so maven is happy.
        '''
        
        sudo('yum -y install java-1.7.0-openjdk java-1.7.0-openjdk-devel')
        
    def install_maven(self):
        '''Downloads and installs maven.
        '''
        
        # download and extract maven
        run('wget http://mirror.symnds.com/software/Apache/maven/maven-3/3.3.3/binaries/apache-maven-3.3.3-bin.tar.gz')
        sudo('tar xzf apache-maven-3.3.3-bin.tar.gz -C /usr/local')
        run('rm apache-maven-3.3.3-bin.tar.gz')
        with cd('/usr/local'):
            sudo('ln -s apache-maven-3.3.3 maven')
        
        # check that mvn command works
        run('/usr/local/maven/bin/mvn -version')
        
    def install_node(self, version='v5.1.1'):
        '''Installs node, npm and forever.
        '''
        
        # download and install from website instead of yum
        run('wget https://nodejs.org/dist/{0}/node-{0}-linux-x64.tar.gz'.format(version))
        sudo('tar xzf node-{0}-linux-x64.tar.gz -C /usr/local'.format(version))
        run('rm -rf node-{0}-linux-x64.tar.gz'.format(version))
        sudo('mv /usr/local/node-{0}-linux-x64 /usr/local/node'.format(version))
        sudo('ln -s /usr/local/node/bin/node /usr/bin/node')
        sudo('ln -s /usr/local/node/bin/npm /usr/bin/npm')
        
        # install forever to run server continuously
        sudo('npm install forever -g')
        sudo('ln -s /usr/local/node/bin/forever /usr/bin/forever')
    
    def set_timezone(self, tz):
        '''Changes the machine's localtime to the desired timezone.
        '''
        
        with cd('/etc'):
            sudo('rm -rf localtime')
            sudo('ln -s {0} localtime'.format(tz))
        
    def update_system(self):
        '''Updates the instance with the latest patches and upgrades.
        '''
        
        sudo('yum -y update')

    def populate_and_upload_template_file(self, data_dict, configHelper, filename, destination,
                                          use_sudo=False, out_filename=None):
        '''Create new data file from a template and then upload it to machine.
        '''

        put(configHelper.write_template(data_dict, filename, out_filename), destination, use_sudo)
        
    def _upload_pg_hba_conf2(self, remote_data_folder, 
                             remote_pg_hba_conf, local_method):
        '''Overwrites pg_hba.conf with specified local method.
        '''
        
        sudo('rm -rf {0}'.format(remote_pg_hba_conf))
        
        if not exists(self.config_dir):
            run('mkdir {0}'.format(self.config_dir))

        self.populate_and_upload_template_file(dict(local_method=local_method),
                                               self._config_helper,
                                               'pg_hba.conf',
                                               self.config_dir)
        
        sudo('mv {0} {1}'.format(unix_path_join(self.config_dir, 'pg_hba.conf'),
                                 remote_data_folder))
        
        sudo('chmod 600 {0}'.format(remote_pg_hba_conf))
        sudo('chgrp postgres {0}'.format(remote_pg_hba_conf))
        sudo('chown postgres {0}'.format(remote_pg_hba_conf))
            

class CentOS6Fab(RHELFab):
    
    def create_non_root_user(self):
        '''Setup a non-root user.
        '''
        
        user_name = self.conf.get('non_root_user')
        
        run('adduser {0}'.format(user_name))
        run('echo {0} | passwd {1} --stdin'.
            format(self.conf.get('non_root_password'),
                   user_name))
        
        # grant sudo access to regular user
        self.populate_and_upload_template_file(dict(non_root_user=user_name),
                                               self._config_helper,
                                               'user-init',
                                               '/etc/sudoers.d',
                                               True)
    
    def install_helpers(self):
        '''Installs various utilities (typically not included with CentOS).
        '''
        
        sudo('yum -y install wget')
        sudo('yum -y install unzip')
        
    def install_postgis(self, db_name, init_sql_path, init_sql_filename):
        '''Downloads and configures PostgreSQL + PostGIS.
        
        Args:
            db_name (string): database name to install PostGIS on
            init_sql_path (string): full path to init_sql file
            init_sql_filename (string): filename of init_sql file
        '''
        
        # get yum squared away
        sudo('rpm -ivh http://yum.postgresql.org/9.3/redhat/rhel-6-x86_64/pgdg-centos93-9.3-1.noarch.rpm')
        
        # install postgresql
        sudo('yum -y install postgresql93 postgresql93-server postgresql93-libs postgresql93-contrib postgresql93-devel')
        
        # make sure yum knows about postgis dependencies
        sudo('rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm')
        
        # install postgis
        sudo('yum -y install postgis2_93')
        
        # initialize db
        sudo('service postgresql-9.3 initdb')
        
        # upload insecure pg_hba.conf
        self._upload_pg_hba_conf('trust')
        
        put(init_sql_path, self.config_dir)
        
        # start postgres
        sudo('service postgresql-9.3 start')
        
        # execute db setup sql
        init_sql_filename = unix_path_join(self.config_dir, init_sql_filename)
        sudo('psql -U postgres -f {0}'.format(init_sql_filename))
        sudo('psql -U postgres -d {0} -c "CREATE EXTENSION postgis;"'.format(db_name))
        
        # switch to more secure pg_hba.conf
        self._upload_pg_hba_conf('md5')
        
        # restart postgres
        sudo('service postgresql-9.3 restart')
        
        # start postgresql on boot
        sudo('chkconfig postgresql-9.3 on')
        
    def setup_iptables_for_port(self, port=3000):
        '''Adds in iptables rules to forward 80 to user-specified port.
        
        Got help from: http://serverfault.com/questions/722270/configuring-centos-6-iptables-to-use-port-80-for-nodejs-app-running-on-port-3000/722282#722282
        
        Args:
            port (int, default=3000): Port to forward to.
        '''
        
        sudo('iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT')
        sudo('iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port {0}'.format(port))
        sudo('iptables -I INPUT 1 -p tcp --dport {0} -j ACCEPT'.format(port))
        sudo('sudo service iptables save')
        
    def _upload_pg_hba_conf(self, local_method):
        '''Overwrites pg_hba.conf with specified local method.
        '''
        
        self._upload_pg_hba_conf2('/var/lib/pgsql/9.3/data', 
                                  '/var/lib/pgsql/9.3/data/pg_hba.conf', local_method)
                    
            
class AmazonLinuxFab(RHELFab):
    
    def install_custom_monitoring(self):
        '''Installs a custom monitoring script to monitor memory and disk utilization.
        '''
        
        # install helpers
        sudo('yum -y install perl-DateTime perl-Sys-Syslog perl-LWP-Protocol-https')
        
        # dl scripts
        run('wget http://aws-cloudwatch.s3.amazonaws.com/downloads/CloudWatchMonitoringScripts-1.2.1.zip')
        sudo('unzip CloudWatchMonitoringScripts-1.2.1.zip -d /usr/local')
        run('rm CloudWatchMonitoringScripts-1.2.1.zip')
        
        # prepare the monitoring crontab        
        cron = 'MAILTO={cron_email}\n'
        cron += '*/5 * * * * /usr/local/aws-scripts-mon/mon-put-instance-data.pl --mem-util --disk-space-util --disk-path=/ --from-cron --aws-access-key-id={aws_access_key_id} --aws-secret-key={aws_secret_key}'
        
        cron_settings = dict(aws_access_key_id=self.conf.get('aws_access_key_id'),
                             aws_secret_key=self.conf.get('aws_secret_access_key'),
                             cron_email=self.conf.get('cron_email'))  
        aws_logging_cron = cron.format(**cron_settings)
            
        # start crontab for aws monitoring
        crontab_update(aws_logging_cron, 'aws_monitoring')
        
    def install_pg(self, init_sql_path, init_sql_filename):
        '''Installs Postgresql and executes some SQL.
        
        Args:
            init_sql_path (string): full path to init_sql file
            init_sql_filename (string): filename of init_sql file
        '''
        
        # install it
        sudo('yum -y install postgresql postgresql-server')
        
        # initialize db
        sudo('service postgresql initdb')
        
        # edit pg_hba for db initialization
        self._upload_pg_hba_conf('trust')
        
        # start postgersql server
        sudo('service postgresql start')
        
        # run init sql
        if not exists(self.config_dir):
            run('mkdir {0}'.format(self.config_dir))
        
        put(init_sql_path, self.config_dir)
        
        init_sql_filename = unix_path_join(self.config_dir, init_sql_filename)
        sudo('psql -U postgres -f {0}'.format(init_sql_filename))
        
        sudo('rm -rf {0}'.format(init_sql_filename))
        
        # switch to more secure pg_hba.conf
        self._upload_pg_hba_conf('md5')
        
        # start postgersql server
        sudo('service postgresql restart')
        
        # start postgresql on boot
        sudo('chkconfig postgresql on')
            
    def _upload_pg_hba_conf(self, local_method):
        '''Overwrites pg_hba.conf with specified local method.
        '''
        
        self._upload_pg_hba_conf2('/var/lib/pgsql9/data', 
                                  '/var/lib/pgsql9/data/pg_hba.conf', local_method)


class FabLogger():
    '''A logger for Fabric that both prints to terminal and saves output to file.
    
    Copied from http://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python
    '''
    
    def __init__(self, filename='fab.log'):
        self.terminal = sys.stdout
        self.filename = filename
        
    def __getattr__(self, attr): 
        return getattr(self.terminal, attr)

    def write(self, message):
        self.terminal.write(message)
        with open(self.filename, 'a') as f:
            f.write(message)
            

def unix_path_join(*args):
    '''Join paths using unix slashes.
    
    Args:
        *args: a list of strings
        
    Returns:
        string: the joined list
    '''
    
    return '/'.join(args)
