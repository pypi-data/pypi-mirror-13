import subprocess
import uuid

from Logger import logger


class TPTCMD(object):
    '''
    Provide OS interface to run bteq and tbuild command.
    '''

    def __init__(self):
        pass

    def run_command(self, command):
        '''
        Run OS command.
        :param command: Command to be run.
        :return: command exit code.
        '''
        ret_val = 0
        try:
            logger.info('Run OS command: {}'.format(command))
            subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError:
            ret_val = -1
        except Exception as e:
            logger.error(str(e))
            ret_val = -2
        return ret_val

    def run_bteq(self, bteq_script, output_file):
        '''
        Run BTEQ script, if successfully, return 0, else return error code.
        :param bteq_script: the bteq script to run.
        :param output_file: the output logfile.
        :return: BTEQ return code.
        '''
        command = 'bteq < {} > {} 2>&1'.format(bteq_script, output_file)
        ret_val = self.run_command(command)
        return ret_val

    def run_tpt(self, tpt_job_script, tpt_job_vars, output_file):
        '''
        Run tbuild script, if successfully loaded, then return 0, else return error code.
        :param tpt_job_script: tbuild script to be run.
        :param tpt_job_vars: tbuild job related variables.
        :param output_file: tbuild run logfile.
        :return: tbuild return code.
        '''
        command = 'tbuild -f {} -v {} -j {} > {} 2>&1'.format(tpt_job_script, tpt_job_vars, str(uuid.uuid1()),
                                                              output_file)
        ret_val = self.run_command(command)
        return ret_val
