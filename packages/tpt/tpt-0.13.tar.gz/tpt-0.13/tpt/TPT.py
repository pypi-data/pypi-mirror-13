from Parser import flatFileParser
from TPTSQL import TPTSQL
from FileMaker import FileMaker
from TPTCMD import TPTCMD
from TDJDBC import TDJDBC
from iniParser import read_global_settings
import uuid
import os
import sys

from Logger import logger


class TPT(object):
    '''
    This class use for controlling the load and export operation.
    '''

    def __init__(self):
        '''
       TPT initialize method, if you need to store your database authentication stored for easy program,
       manually store your database authentication in ${HOME}/.td_user_auth_file.
       File Format:
       [Connect_Info]
       host=your_td_host            # TD host, can be IP addr or full DNS
       user=your_td_username        # TD user
       password=your_td_password    # TD user password
       '''
        self.default_auth_ini = os.path.join(os.environ['HOME'], '.td_user_auth_file')
        self.datafiles = []
        self.sep = ','
        self.has_header = True
        self.column_names = None
        self.idx_columns = None
        self.driver = None
        self.sample_size = 1000
        self.keywords_file = 'keywords.txt'
        self.tpt_export_data_file = ''
        self.export_sql_stmt = ''
        self.export_fs = ','
        self.use_exist_table = False

        if os.path.exists(self.default_auth_ini):
            auth_dict = read_global_settings(self.default_auth_ini, 'Connect_Info')
            self.host = auth_dict.get('host')
            self.user = auth_dict.get('user')
            self.password = auth_dict.get('password')
            logger.debug('Reading TD auth info from auth file {}.'.format(self.default_auth_ini))
        else:
            self.host = None
            self.user = None
            self.password = None

        self.FILES = {'job_run_dir': None,
                      'bteq_script': None,
                      'bteq_logfile': None,
                      'tbuild_logfile': None,
                      'tpt_job_script': None,
                      'tpt_job_vars': None,
                      'tpt_job_export_script': None,
                      'tpt_job_export_vars': None,
                      'tpt_export_data_file': None
                      }
        self.driver_ddl = None
        self.columns_info = None

    def set_use_exist_table(self, use_exist_table=False):
        self.use_exist_table = use_exist_table
        logger.info('Use exist table setting: {}'.format(self.use_exist_table))

    def remove_file(self, file_path):
        if file_path and os.path.exists(file_path):
            logger.debug('Remove file {} ...'.format(file_path))
            os.remove(file_path)

    def remove_files(self):
        self.remove_file(self.FILES.get('bteq_script'))
        self.remove_file(self.FILES.get('tpt_job_script'))
        self.remove_file(self.FILES.get('tpt_job_vars'))
        self.remove_file(self.FILES.get('tpt_job_export_script'))
        self.remove_file(self.FILES.get('tpt_job_export_vars'))

    def set_sample_size(self, sample_size):
        self.sample_size = sample_size

    def set_td_auth(self, host, user, password):
        '''
        Set Teradata connect information, such TD server host, user and password.
        :param host: Teradata server host, ip address or FQDN.
        :param user: Teradata user name.
        :param password: Teradata  user password.
        :return: None
        '''
        self.host = host
        self.user = user
        self.password = password
        logger.info('Set TD auth info.')
        logger.debug('host = {}'.format(self.host))
        logger.debug('user = {}'.format(self.user))
        logger.debug('password = *******')

    def set_export_datafile_info(self, sql_stmt, sep=',', tpt_export_data_file=''):
        '''
        Set the export destination file attribute.
        :param sql_stmt: The SQL stmt for the data set to be exported.
        :param sep: Destination data file field delimiter.
        :return: None
        '''
        self.export_sql_stmt = sql_stmt
        self.export_fs = sep
        if tpt_export_data_file and tpt_export_data_file != '':
            self.tpt_export_data_file = tpt_export_data_file

    def set_datafile_info(self, datafiles, column_names=None, sep=',', has_header=True):
        '''
        Set the data file information, such as data file path, field delimiter, has header line or not.
        If no header line specified, can provide the column name list.
        :param datafiles: data file to be loaded.
        :param column_names: Column name list, if no header line in data file, use the names as schema names
        :param sep: Data file field delimiter. Only single character is support, such as :, |, \t, and etc.
        :param has_header: If the data file has header line use True, or use False.
        :return: None
        '''
        if isinstance(datafiles, str) and os.path.exists(datafiles):
            logger.info('Add data file {} to load.'.format(datafiles))
            self.datafiles.append(datafiles)
        elif isinstance(datafiles, list):
            logger.info('Add a list of data files to load. files {}.'.format(datafiles))
            self.datafiles = datafiles
        else:
            logger.error('No data files added.')
            logger.debug('datafiles = {}'.format(datafiles))
            sys.exit(100)
            self.datafiles = []

        self.column_names = column_names
        self.sep = sep
        self.has_header = has_header

        logger.debug('datafiles = {}'.format(self.datafiles))
        logger.debug('column_names = {}'.format(str(self.column_names)))
        logger.debug('sep = {}'.format(self.sep))
        logger.debug('has_header = {}'.format(self.has_header))

    def set_driver(self, driver):
        '''
        Set the driver for load operation. In another word, the final table name. Which table will contains the loaded data
        from the given source data file. But if the given table name already exist in database, the final table name will
        be add suffix.
        :param driver: The final table name, format databasename.tablename .
        :return: None
        '''
        self.driver = driver
        logger.debug('driver = {}'.format(driver))

    def set_idx_columns(self, idx_columns):
        '''
        Set the index column names list. These names and list order will be use to create the primary index.
        :param idx_columns: Index column names for primary index.
        :return: None
        '''
        self.idx_columns = idx_columns
        logger.debug('idx_columns = {}'.format(str(self.idx_columns)))

    def load(self):
        '''
        Do the load process. Load data from the given data file into a Teradata table.
        Make sure the given TD tablename does not exist in database or the tablename will be rename with suffix to make
        no danger to the exist table.
        :return: return_code
                    0  -  Load process successfully.
                    1  -  Load process failed.
                    2  -  Create final table failed.
        '''
        return_code = 0

        p = flatFileParser()
        p.add_datafiles(self.datafiles)
        p.set_sep(self.sep)
        p.set_has_header(has_header=self.has_header)
        p.set_columns(self.column_names)
        p.set_sample_size(self.sample_size)
        p.set_keywords_file(keywords_file=self.keywords_file)
        columns_info = p.parser()
        self.columns_info = columns_info

        tptsql = TPTSQL()

        if not self.use_exist_table:
            tdjdbc = TDJDBC(host=self.host, user=self.user, password=self.password)
            tdjdbc.get_connect()
            while tdjdbc.is_table_exists(full_table_name=self.driver):
                self.driver = '{}_{}'.format(self.driver, str(uuid.uuid1())[:3])
                logger.info('Try new table name {}...'.format(self.driver))
            tdjdbc.close_connect()
            tptsql.set_driver(self.driver)
            tptsql.set_columns_info(columns_info)
            tptsql.set_idx_columns(self.idx_columns)
            logger.debug('Idx column list: {}'.format(self.idx_columns))
            ddl = tptsql.get_ddl()
            self.driver_ddl = ddl
            logger.info('Make the destination table as {}'.format(self.driver))

        fm = FileMaker()
        fm.set_has_header(self.has_header)
        fm.set_db_auth(host=self.host, user=self.user, password=self.password)
        if not self.use_exist_table:
            fm.make_bteq_script(stmts=[ddl])
        fm.make_tpt_job_script()
        fm.make_tpt_job_vars(src_datafiles=self.datafiles[0], sep=self.sep, dest_tablename=self.driver)
        logger.info('Making tpt load job script successfully.')

        self.FILES['job_run_dir'] = fm.job_run_dir
        self.FILES['bteq_script'] = fm.bteq_script
        self.FILES['bteq_logfile'] = fm.bteq_logfile
        self.FILES['tbuild_logfile'] = fm.tbuild_logfile
        self.FILES['tpt_job_script'] = fm.tpt_job_script
        self.FILES['tpt_job_vars'] = fm.tpt_job_vars

        self.sample_size = p.sample_rows
        logger.info('Sample Rows count: {}'.format(self.sample_size))

        tptcmd = TPTCMD()
        if not self.use_exist_table:
            logger.info("BTEQ run logfile {} ...".format(fm.bteq_logfile))
            retval = tptcmd.run_bteq(fm.bteq_script, fm.bteq_logfile)
        else:
            retval = 0
        if retval == 0:
            logger.info("Create table {} successfully.".format(tptsql.driver))
            logger.info("tbuild run logfile {} ...".format(fm.tbuild_logfile))
            retval_1 = tptcmd.run_tpt(fm.tpt_job_script, fm.tpt_job_vars, fm.tbuild_logfile)
            if retval_1 == 0:
                logger.info('Load data successfully.')
            else:
                logger.error("Load data failed.")
                return_code = 1
        else:
            logger.error("Create table {} failed.".format(tptsql.driver))
            return_code = 2

        logger.info('Working directory: {}'.format(self.FILES['job_run_dir']))
        # logger.info('BTEQ script: {}'.format(self.FILES['bteq_script']))
        logger.info('BTEQ run logfile: {}'.format(self.FILES['bteq_logfile']))
        logger.info('tpt run logfile: {}'.format(self.FILES['tbuild_logfile']))
        # logger.info('tpt job configure file: {}'.format(self.FILES['tpt_job_script']))
        # logger.info('tpt job variable file: {}'.format(self.FILES['tpt_job_vars']))
        # self.remove_files()
        if return_code == 0:
            logger.info('Query Table Definition: show table {};'.format(self.driver))
            logger.info('Query Data: select * from {};'.format(self.driver))
        logger.debug('Load process return code: {}'.format(return_code))
        return return_code

    def export(self):
        '''
        Do the export process. Export the data set from given SQL to a text data file.
        :return: return_code
                    0  - Export process successfully.
                    1  - Export process failed.
        '''
        return_code = 0
        fm = FileMaker()
        fm.set_db_auth(host=self.host, user=self.user, password=self.password)
        fm.make_tpt_export_script()
        fm.make_tpt_export_vars(sql_stmt=self.export_sql_stmt, sep=self.export_fs,
                                tpt_export_data_file=self.tpt_export_data_file)

        self.FILES['job_run_dir'] = fm.job_run_dir
        self.FILES['tbuild_logfile'] = fm.tbuild_logfile
        self.FILES['tpt_job_export_script'] = fm.tpt_job_export_script
        self.FILES['tpt_job_export_vars'] = fm.tpt_job_export_vars
        self.FILES['tpt_export_data_file'] = fm.tpt_export_data_file
        logger.debug('fm.tpt_export_data_file = {}'.format(fm.tpt_export_data_file))

        tptcmd = TPTCMD()
        retval = tptcmd.run_tpt(fm.tpt_job_export_script, fm.tpt_job_export_vars, fm.tbuild_logfile)
        if retval == 0:
            logger.info('Export Job finish successfully.')
        else:
            logger.error('Export Job finish failed.')
            return_code = 1

        logger.info('Working directory: {}'.format(self.FILES['job_run_dir']))
        logger.info('Export SQL STMT: {}'.format(self.export_sql_stmt))
        logger.info('Destination Data File Separator: {}'.format(self.export_fs))
        logger.info('tpt export run logfile: {}'.format(self.FILES['tbuild_logfile']))
        # logger.info('tpt export job configure file: {}'.format(self.FILES['tpt_job_export_script']))
        # logger.info('tpt export job variable file: {}'.format(self.FILES['tpt_job_export_vars']))
        logger.info('tpt export destination data file: {}'.format(self.FILES['tpt_export_data_file']))
        self.remove_files()
        logger.debug('Load process return code: {}'.format(return_code))
        return return_code

    def main(self):
        # column_names = ['username', 'passwd', 'uid', 'gid', 'user_desc', 'home_path', 'shell_path']
        # self.set_datafile_info(datafiles='/etc/passwd', column_names=column_names, sep=':', has_header=False)
        self.set_datafile_info(datafiles='/etc/passwd', sep=':', has_header=False)
        self.set_driver('PP_OAP_SELLER_BI_TEST_T.el_passwd12346')
        # self.set_idx_columns(['uid', 'username'])
        self.load()


if __name__ == '__main__':
    tpt = TPT()
    tpt.main()
