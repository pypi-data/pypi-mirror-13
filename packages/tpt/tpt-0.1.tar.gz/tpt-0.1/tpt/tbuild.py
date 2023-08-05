from Parser import flatFileParser
from TPTSQL import TPTSQL
from FileMaker import FileMaker
from TPTCMD import TPTCMD


def main():
    p = flatFileParser()
    datafiles = ['/etc/passwd']
    p.add_datafiles(datafiles)
    p.set_sep(':')
    p.set_has_header(has_header=False)
    p.set_columns(['username', 'passwd', 'uid', 'gid', 'user_desc', 'home_path', 'shell_path'])
    columns_info = p.parser()

    tptsql = TPTSQL()
    tptsql.set_driver('pp_oap_seller_bi_test_t.el_passwd_1234567')
    tptsql.set_columns_info(columns_info)
    tptsql.set_idx_columns(['uid'])
    ddl = tptsql.get_ddl()

    fm = FileMaker()
    fm.set_db_auth(user='pp_srm_bi_user', password='_Hello_PP_5211')
    fm.make_bteq_script(stmts=[ddl])
    fm.make_tpt_job_script()
    fm.make_tpt_job_vars(p.datafiles[0], p.sep, tptsql.driver)

    tptload = TPTCMD()
    print "BTEQ run logfile {} ...".format(fm.bteq_logfile)
    retval = tptload.run_bteq(fm.bteq_script, fm.bteq_logfile)
    if retval == 0:
        print "Create table {} successfully.".format(tptsql.driver)
        print "tbuild run logfile {} ...".format(fm.tbuild_logfile)
        retval_1 = tptload.run_tpt(fm.tpt_job_script, fm.tpt_job_vars, fm.tbuild_logfile)
        if retval_1 == 0:
            print 'Load data successfully.'
        else:
            print "Load data failed."
    else:
        print "Create table {} failed.".format(tptsql.driver)


if __name__ == '__main__':
    main()
