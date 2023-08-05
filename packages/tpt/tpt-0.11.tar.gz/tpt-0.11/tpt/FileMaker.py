import os
import uuid

from Logger import logger


class FileMaker(object):
    '''
    This class use for create bteq script, tpt configure file and tpt variable file.
    '''

    def __init__(self, base_dir='/tmp', has_header=True):
        self.base_dir = base_dir
        self.job_run_dir = os.path.join(self.base_dir, 'tbuild-{}'.format(str(uuid.uuid1())))

        if not os.path.exists(self.job_run_dir):
            os.makedirs(self.job_run_dir)
            logger.debug('Make directory {}'.format(self.job_run_dir))

        self.bteq_script = os.path.join(self.job_run_dir, 'bteq.script')
        self.tpt_job_script = os.path.join(self.job_run_dir, 'tpt_job.script')
        self.tpt_job_export_script = os.path.join(self.job_run_dir, 'tpt_export_job.script')
        self.tpt_job_vars = os.path.join(self.job_run_dir, 'tpt_job_vars.txt')
        self.tpt_job_export_vars = os.path.join(self.job_run_dir, 'tpt_export_job_vars.txt')
        self.bteq_logfile = os.path.join(self.job_run_dir, 'bteq.log')
        self.tbuild_logfile = os.path.join(self.job_run_dir, 'tbuild.log')
        self.has_header = has_header
        self.tpt_export_data_file = os.path.join(self.job_run_dir, 'tpt_export_job_data_file.csv')

    def set_has_header(self, has_header):
        '''
        Set if the source data file has header line or not.
        '''
        self.has_header = has_header

    def set_db_auth(self, host='simba.vip.paypal.com', user='', password=''):
        '''
        Set Teradata Auth info, such as TD server host, username and password.
        '''
        self.host = host
        self.user = user
        self.password = password

    def set_tpt_export_data_file_path(self, tpt_export_data_file):
        '''
        Set the exported destination data file path.
        '''
        if tpt_export_data_file and tpt_export_data_file != '':
            self.tpt_export_data_file = tpt_export_data_file
            logger.debug('Set tpt export destination data file to {}'.format(self.tpt_export_data_file))

    def make_bteq_script(self, stmts=[]):
        '''
        Create BTEQ run script.
        '''
        stmts = [sql.strip(';') for sql in stmts]
        sql_text = ";\n".join(stmts) + ';'
        text = """
.LOGON {}/{},{};
.SET width 1050;
{}
.LOGOFF;
.QUIT;
""".format(self.host, self.user, self.password, sql_text)
        logger.debug('Making BTEQ script file: {}'.format(self.bteq_script))
        with open(self.bteq_script, 'w') as f:
            f.write(text)

        return self.bteq_script

    def make_tpt_job_script(self):
        '''
        Create tbuild load job script file.
        '''
        attr_options = ""
        if self.has_header:
            attr_options += ", SkipRows=1"
        text = """
using character set ASCII
         
define job tpt_file_to_table
(
    set MaxDecimalDigits = 38;
         
    set LogTable    = @TargetTable || '_LogTable';
    set ErrorTable1 = @TargetTable || '_ErrorTable1';
    set ErrorTable2 = @TargetTable || '_ErrorTable2';
    set WorkTable   = @TargetTable || '_WorkTable';
     
    step cleanup
    (
        apply
         
        ('call pp_monitor.drop_table (''' || @LogTable      || ''');')
       ,('call pp_monitor.drop_table (''' || @ErrorTable1   || ''');')
       ,('call pp_monitor.drop_table (''' || @ErrorTable2   || ''');')
       ,('call pp_monitor.drop_table (''' || @WorkTable     || ''');')
                
        to operator ($DDL);
    )
    ;
   
    step main
    (
        apply $insert to operator ($load)
        select * from operator ($file_reader ATTR (
              QuotedData='Optional'
              {}
        ))
        ;
    )
    ;
)
;
""".format(attr_options)
        # SkipRows=1
        # ,OpenQuoteMark='"'
        # ,CloseQuoteMark='"'
        # , AcceptMissingColumns = 'YesWithoutLog'
        # , AcceptExcessColumns = 'YesWithoutLog'
        logger.debug('Making TPT job configure file: {}'.format(self.tpt_job_script))
        with open(self.tpt_job_script, 'w') as f:
            f.write(text)

        return self.tpt_job_script

    def make_tpt_job_vars(self, src_datafiles, sep, dest_tablename):
        '''
        Make TPT job variable file.
        :param src_datafiles: Source data file to be loaded.
        :param sep: Field delimiter.
        :param dest_tablename: Which table to load data into.
        :return: TPT job variable file.
        '''
        text = """
SourceFileName         = '{}'
,SourceFormat           = 'Delimited'
,SourceTextDelimiter    = '{}'
,TargetTdpId            = '{}'
,TargetUserName         = '{}'
,TargetUserPassword     = '{}'
,TargetTable            = '{}'        
""".format(src_datafiles, sep, self.host, self.user, self.password, dest_tablename)
        logger.debug('Making TPT job variable file: {}'.format(self.tpt_job_vars))
        with open(self.tpt_job_vars, 'w') as f:
            f.write(text)

        return self.tpt_job_vars

    def make_tpt_export_script(self):
        '''
        Create tbuild export script file.
        '''
        logger.info('Making TPT export job configure file {}'.format(self.tpt_job_export_script))
        text = """
using character set UTF8

define job tpt_export_table_to_file_{}
(
    set MaxDecimalDigits = 38;

    apply to operator ($file_writer)
    select * from operator ($export)
    ;
);
""".format(str(uuid.uuid1())[:5])
        with open(self.tpt_job_export_script, 'w') as f:
            f.write(text)
        return self.tpt_job_export_script

    def make_tpt_export_vars(self, sql_stmt, sep=',', tpt_export_data_file=''):
        '''
        Create tbuild export variable file.
        :param sql_stmt: Define the SQL statement for the data set that need to be exported.
        :param sep: The destination data file field delimiter.
        :return: The tpt export variable file path.
        '''
        logger.info('Making TPT export job variable file {}'.format(self.tpt_job_export_vars))
        logger.debug('sql_stmt: {}'.format(sql_stmt))
        logger.debug('sep: {}'.format(sep))
        logger.debug('tpt_export_data_file: {}'.format(tpt_export_data_file))
        self.set_tpt_export_data_file_path(tpt_export_data_file)

        text = """
SourceTdpId            = '{}'
,SourceUserName         = '{}'
,SourceUserPassword     = '{}'
,SelectStmt             = '{}'
,TargetFileName         = '{}'
,TargetFormat           = 'delimited'
,TargetTextDelimiter    = '{}'
""".format(self.host, self.user, self.password, sql_stmt, self.tpt_export_data_file, sep)
        with open(self.tpt_job_export_vars, 'w') as f:
            f.write(text)
        return self.tpt_job_export_vars
