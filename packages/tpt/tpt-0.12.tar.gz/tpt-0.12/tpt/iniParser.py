from ConfigParser import ConfigParser
import re


def read_global_settings(conf_fn, sect_name):
    '''
    Read Section config from ini configure file
    conf_fn   --  the ini configure file
    sect_name --  the name the section which you want to read configure from
    '''
    config_dict = None
    try:
        cf = ConfigParser()
        cf.read(conf_fn)
        config_dict = dict(cf.items(sect_name))
    except IOError as (errno, strerror):
        print "I/O error({0}): {1}".format(errno, strerror)
    except:
        print "Parser config file %s error, please check." % conf_fn
    else:
        # first time replace variables
        d_var = {}
        for k, v in config_dict.items():
            config_dict[k] = v.strip(''''"''')
            # m=re.match(r'\$\{([a-zA-Z_][a-zA-Z_0-9]+)\}',v)
            m = re.findall(r'\$\{([a-zA-Z_][a-zA-Z_0-9]+)\}', config_dict[k])
            if m:
                d_var[k] = m

        for k in d_var.keys():
            k_conf = config_dict[k]
            for tmp_var in d_var[k]:
                # print "tmp_var=%s" % tmp_var
                k_conf = re.sub(r'\$\{' + tmp_var + r'\}', config_dict[tmp_var], k_conf)
                # print "k_conf=%s" % k_conf
            config_dict[k] = k_conf

        # Second time replace variables
        d_var = {}
        for k, v in config_dict.items():
            m = re.findall(r'\$\{([a-zA-Z_][a-zA-Z_0-9]+)\}', config_dict[k])
            if m:
                d_var[k] = m

        for k in d_var.keys():
            k_conf = config_dict[k]
            for tmp_var in d_var[k]:
                k_conf = re.sub(r'\$\{' + tmp_var + r'\}', config_dict[tmp_var], k_conf)
            config_dict[k] = k_conf

    return config_dict
