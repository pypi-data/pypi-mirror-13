import os
from Logger import logger
'''
Define where to find the TD JDBC library jars.
1. Environment variable: TD_JDBC_LIB_PATH, if this environment variable is set, then make sure the
TD JDBC library jars exists in the directory, or go next.

2. If TD_JDBC_LIB_PATH environment variable is set, the use common directory /opt/td_jdbc_lib, but if
directory /opt/td_jdbc_lib exist, make sure the TD JDBC library jars exists in the directory, or go next.

3. Last use the current working directory as the directory which contains TD JDBC library jars, if none
of the above is meet, make the tdgssconfig.jar and terajdbc4.jar exist in current working directory.
'''

TD_JDBC_LIB_PATH = os.environ.get('TD_JDBC_LIB_PATH')
if TD_JDBC_LIB_PATH == '' or not TD_JDBC_LIB_PATH:
    TD_JDBC_LIB_PATH = '/opt/td_jdbc_lib'
    logger.debug('Make sure directory {} exists, and Teradata JDBC library jars exists.'.format(TD_JDBC_LIB_PATH))

if not os.path.exists(TD_JDBC_LIB_PATH):
    TD_JDBC_LIB_PATH = os.getcwd()

logger.debug('Teradata JDBC jars should be reside in directory {}'.format(TD_JDBC_LIB_PATH))

JDBC_CONF_PATH = os.path.join(TD_JDBC_LIB_PATH, 'tdgssconfig.jar')
JDBC_PATH = os.path.join(TD_JDBC_LIB_PATH, 'terajdbc4.jar')
DATA_SOURCE = 'jdbc:teradata://TD_Server_IPAddr_or_DNS'
