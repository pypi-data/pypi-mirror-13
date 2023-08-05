import pandas as pd

import os
from Logger import logger
import re
import string


class flatFileParser():
    '''
    The class use for parser flat file schema.
    '''

    def __init__(self, datafiles=[], sep=',', has_header=True, columns=None):
        self.datafiles = datafiles
        self.sep = sep
        self.has_header = has_header
        self.columns = columns
        # Sample Row lines, if file row count less than Sample Row lines, proccess all lines.
        self.sample_rows = 50000
        self.quotechar = '"'

        self.keywords_file = None
        self.all_keywords = []

    def set_keywords_file(self, keywords_file='keywords.txt'):
        self.keywords_file = keywords_file

    def get_all_td_keywords(self):
        '''
        Retrieve keyword from keyword file.
        '''
        if os.path.exists(self.keywords_file):
            logger.info('Read TD keywords from file {}'.format(self.keywords_file))
            with open(self.keywords_file, 'r') as f:
                all_lines = f.readlines()
                self.all_keywords = []
                for line in all_lines:
                    if len(line.strip()) > 0:
                        self.all_keywords += [item.strip().upper() for item in line.split()]
                # logger.info('Keywords: {}'.format(self.all_keywords))
                logger.info('Total keyword count {}'.format(len(self.all_keywords)))

    def set_sample_size(self, sample_size=1000):
        self.sample_rows = sample_size

    def add_datafiles(self, datafiles):
        '''
        add data files to be proceed.
        '''
        if isinstance(datafiles, list):
            self.datafiles += datafiles
        elif isinstance(datafiles, str):
            self.datafiles = datafiles.split(',')
        else:
            self.datafiles = []

    def set_sep(self, sep):
        '''
        set the field seperator.
        '''
        self.sep = sep

    def set_has_header(self, has_header=True):
        '''
        set if the data files has header line, True or False
        '''
        self.has_header = has_header

    def set_columns(self, columns):
        '''
        if no header line, need to set the column names list, column name need to match the column position
        '''
        self.columns = columns

    def make_column_names(self):
        '''
        Generate column names list if the data file has no header line and also do not specified the column names list.
        If has no header line and give the column names list, use the given column names list.
        '''
        column_count = 0
        column_name_prefix = 'col_'
        # data file has no header line, and also do not specified column name list.
        if not self.has_header and not self.columns:
            # make the column names according to the first line in the first data file.
            self.columns = []
            df = pd.read_csv(self.datafiles[0], sep=self.sep, nrows=1)
            column_count = len(df.columns)
            for i in range(column_count):
                self.columns.append(column_name_prefix + str(i).zfill(4))

    def judge_sample_size(self):
        '''
        Judge the sample size according to the first data file lines and self.sample_rows.
        The the first data file row count less than self.sample_rows, then process all of the first data file lines.
        '''
        buf_size = 1024 * 1024
        row_count = 0
        with open(self.datafiles[0], 'r') as f:
            read_f = f.read
            buf = read_f(buf_size)
            while buf:
                row_count += buf.count('\n')
                if self.sample_rows < row_count:
                    break
                buf = read_f(buf_size)
        if self.sample_rows > row_count:
            self.sample_rows = row_count

        logger.info('Data file sample size: {}'.format(self.sample_rows))

    def parser(self):
        '''
        Only tries to parser the first data file in the data files list.
        Return the flat file schema, such as each field name, data type and field maximum length if is a string.
        result = [{'field_name':'xx', 'data_type':'yy', 'is_string':True_or_False, 'max_len':0},]
        '''
        result = []
        self.make_column_names()
        self.judge_sample_size()
        names = self.columns
        dataframe = pd.read_csv(self.datafiles[0], sep=self.sep, quotechar=self.quotechar,
                                names=names, nrows=self.sample_rows)

        column_dt = dataframe.dtypes.to_dict()

        self.get_all_td_keywords()

        for column_name in dataframe.columns:
            field_name = column_name
            bad_chars = ': '
            if bad_chars in field_name:
                field_name = field_name.replace(bad_chars, '_')
                logger.warning('Remove bad character "{}" from "{}"'.format(bad_chars, column_name))
            if ' ' in field_name:
                field_name = field_name.replace(' ', '_')
                logger.warning('Remove space from field name "{}"'.format(column_name))

            # Remove any punctuation character from field name.
            for char in string.punctuation:
                if char == '_':
                    continue
                if char in field_name:
                    field_name = field_name.replace(char, '')
                    logger.warning('Remove punctuation character "{}" from "{}"'.format(char, column_name))

            m = re.match(r'^\d+', field_name)
            if m:
                field_name = '_{}'.format(field_name)
                logger.warning('Field name start with digital number.')

            if field_name.upper() in self.all_keywords:
                old_field_name = field_name
                field_name = '__{}'.format(field_name)
                logger.warning('Field name {} is a TD keyword. Change it to {}'.format(old_field_name, field_name))

            if column_name != field_name:
                logger.warning('Change old {} to {}'.format(column_name, field_name))
            date_type = column_dt[column_name].name
            is_string = False
            if column_dt[column_name].name == 'object':
                date_type = 'string'
                is_string = True
            max_len = dataframe[column_name].map(lambda x: len(str(x))).max()
            e = {'field_name': field_name, 'data_type': date_type, 'is_string': is_string, 'max_len': max_len}
            result.append(e)
        return result


if __name__ == '__main__':
    p = flatFileParser()
    datafile = ['/common/tpt-tool/ttquery_dataset.csv']
    p.add_datafiles(datafile)
    p.set_sep(',')
    p.set_has_header(has_header=True)
    p.parser()
