try:
    input = raw_input
except NameError: 
    pass

from string import Formatter
import ConfigParser
import os


class DefaultConfig:
    
    def __init__(self, config_parser):
        self.config_parser = config_parser
        
    def get(self, key):
        return self.config_parser.get('DEFAULT', key)

    def make_params_for_template(self, template_filename):
        out = dict()
        with open(template_filename) as f:
            template = f.read()

        for key in [i[1] for i in Formatter().parse(template)]:
            try:
                out[key] = self.get(key)
            except:
                out[key] = None

        return out


class ConfigHelper:
    
    def __init__(self, config_dir, config_template_dir):
        self.config_dir = config_dir
        self.config_template_dir = config_template_dir
        try:
            os.makedirs(config_dir)
        except:
            pass
        
    def get_config(self, config_type):
        '''Creates new instance of DefaultConfig for a config file
        
        Returns:
            DefaultConfig: the DefaultConfig for the config type
        '''
        
        config_filename = '{0}.ini'.format(config_type)
        config_filename = os.path.join(self.config_dir, config_filename)
        if not os.path.exists(config_filename):
            self.setup(config_type)
            
        config = ConfigParser.ConfigParser()
        config.read(config_filename)
        return DefaultConfig(config)
    
    def setup(self, config_type):
        '''Helps user create config file based off of template.
        User must manually enter stuff.
        '''

        print('-----------------')
        print('Setting up config for {0}'.format(config_type))              
              
        conf = dict()
        config_filename = '{0}.ini'.format(config_type)
        
        with open(os.path.join(self.config_template_dir, config_filename)) as f:
            for line in f:
                if line.find('=') > 0:
                    conf_key = line[:line.find('=')].strip()
                    conf[conf_key] = input('Please enter {0}: '.format(conf_key))
                
        conf_writer = ConfigParser.ConfigParser()
        for k in conf:
            conf_writer.set('DEFAULT', k, conf[k])
        
        with open(os.path.join(self.config_dir, config_filename), 'w') as f:
            conf_writer.write(f)
        
    def write_template(self, params, in_filename, out_filename=None):
        '''Writes a template with values
        
        Args:
            params (dict): a dictionary of values to fill in
            in_filename (string): filename to use
            out_filename (string, optional): optional different output filename
        
        Returns:
            string: path to written file
        '''
        
        if out_filename is None:
            out_filename = in_filename
            
        with open(os.path.join(self.config_template_dir, in_filename)) as f:
            template = f.read()
                
        out_file = os.path.join(self.config_dir, out_filename)
        with open(out_file, 'wb') as f:
            f.write(template.format(**params))
            
        return out_file
