import os

TD_JDBC_LIB_PATH = os.environ.get('TD_JDBC_LIB_PATH')
if TD_JDBC_LIB_PATH == '' or not TD_JDBC_LIB_PATH:
   TD_JDBC_LIB_PATH = '/opt/td_jdbc_lib'
JDBC_CONF_PATH = os.path.join(TD_JDBC_LIB_PATH, 'tdgssconfig.jar')
JDBC_PATH = os.path.join(TD_JDBC_LIB_PATH, 'terajdbc4.jar')
DATA_SOURCE = 'jdbc:teradata://simba.vip.paypal.com'