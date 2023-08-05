from Logger import logger


class TPTSQL():
    def __init__(self, driver='', columns_info=[], pi_columns=[]):
        self.driver = driver
        # columns_info=[{'field_name':'xx', 'data_type':'yy', 'is_string':True_or_False, 'max_len':0},]
        self.columns_info = columns_info
        # pi_columns=['field1_name', 'field2_name']
        self.pi_columns = pi_columns
        self.databasename = ''
        self.tablename = ''
        self.new_add_len = 30

    def set_driver(self, driver):
        self.driver = driver
        e = self.driver.split('.')
        if len(e) == 2:
            self.databasename = e[0]
            self.tablename = e[1]
        else:
            logger.info("Invalid driver_name format, value {}.".format(self.driver))

    def set_columns_info(self, columns_info):
        '''
        Set columns information.
        '''
        self.columns_info = columns_info

    def set_idx_columns(self, pi_columns):
        '''
        Set the primary index column name list.
        '''
        self.pi_columns = pi_columns

    def get_column_metadata(self):
        '''
        Get column metadata.
        '''
        # column_metadata = [{'name':field_name, 'data_type':data_type}, ...]
        column_metadata = []
        for col in self.columns_info:
            field_name = col['field_name']
            data_type = ''
            if col['is_string']:
                data_type = 'VARCHAR({}) CHARACTER SET UNICODE NOT CASESPECIFIC'.format(
                    col['max_len'] + self.new_add_len)
            else:
                if col['data_type'] in ('float64', 'float'):
                    data_type = 'DECIMAL(18,4)'
                elif col['data_type'] in ('int64', 'int'):
                    if col['max_len'] >= 15:
                        data_type = 'VARCHAR({}) CHARACTER SET UNICODE NOT CASESPECIFIC'.format(
                            col['max_len'] + self.new_add_len)
                    elif col['max_len'] <= 3:
                        data_type = 'INT'
                    else:
                        data_type = 'BIGINT'
            e = {'name': field_name, 'data_type': data_type}
            column_metadata.append(e)
        return column_metadata

    def get_ddl(self):
        '''
        Make Table DDL stmt.
        '''
        idx_stmt = 'NO PRIMARY INDEX'
        if self.pi_columns and len(self.pi_columns) > 1:
            idx_stmt = 'UNIQUE PRIMARY INDEX (' + ', '.join(self.pi_columns) + ')'
        columns = []
        column_metadata = self.get_column_metadata()
        for col in column_metadata:
            columns.append('{} {}\n'.format(col['name'], col['data_type']))
        column_stmt = ','.join(columns)

        ddl = '''
CREATE MULTISET TABLE {}.{} ,NO FALLBACK ,
NO BEFORE JOURNAL,
NO AFTER JOURNAL,
CHECKSUM = DEFAULT,
DEFAULT MERGEBLOCKRATIO
(
    {}
)
{}'''.format(self.databasename, self.tablename, column_stmt, idx_stmt)

        return ddl
