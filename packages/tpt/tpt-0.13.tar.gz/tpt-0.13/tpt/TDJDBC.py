import settings
import jaydebeapi


class TDJDBC(object):
    '''
    This class use for TD connect handling through JDBC.
    '''
    def __init__(self, host, user, password):
        self.driver = 'com.teradata.jdbc.TeraDriver'
        self.conn = None
        self.host = host
        self.jdbc_url = 'jdbc:teradata://{}'.format(host)
        self.user = user
        self.password = password
        self.cursor = None
        self.jdbc_jars = [settings.JDBC_CONF_PATH, settings.JDBC_PATH]

    def set_auth(self, host, user, password):
        '''
        Set TD connect auth information, such as host, username and password.
        :param host: The TD server host.
        :param user: The TD auth username.
        :param password: The TD auth password.
        :return: None
        '''
        self.host = host
        self.jdbc_url = 'jdbc:teradata://{}'.format(self.host)
        self.user = user
        self.password = password

    def get_connect(self):
        '''
        Get TD connection through JDBC.
        :return: TD connection object.
        '''
        self.conn = jaydebeapi.connect(self.driver, [self.jdbc_url, self.user, self.password], self.jdbc_jars)
        self.cursor = self.conn.cursor()
        return self.conn

    def close_connect(self):
        '''
        Close connect related objects.
        :return:
        '''
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def is_table_exists(self, full_table_name=None, databasename=None, tablename=None):
        '''
        Judge if the given table exists or not.
        :param full_table_name: The full table name. valid format: databasename.tablename.
        :param databasename: Which database the table reside in.
        :param tablename: The table name.
        :return: If the given table exists in the database, return True, or return False.
        '''
        _databasename = None
        _tablename = None
        if '.' in full_table_name:
            e = full_table_name.split('.')
            _databasename = e[0]
            _tablename = e[1]
        elif databasename and tablename:
            _databasename = databasename
            _tablename = tablename
        else:
            return False

        sql = """select 1 as "result" from dbc.tables where databasename='{}' and tablename='{}'""".format(
            _databasename, _tablename)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if result:
            return True
        else:
            return False
