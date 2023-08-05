from tpt.TPT import TPT

def testLoad():
   tpt = TPT()
   #tpt.set_datafile_info(datafiles='/tmp/stamp_id_2014_01_12.csv', sep=',', has_header=True)
   #tpt.set_datafile_info(datafiles='/tmp/devices.csv', sep=',', has_header=True)
   #tpt.set_datafile_info(datafiles='/tmp/CurrentNames.csv', sep=',', has_header=False)
   #tpt.set_datafile_info(datafiles='/tmp/SIC2003.csv', sep=',', has_header=True)
   #tpt.set_datafile_info(datafiles='/tmp/SIC03to80.csv', sep=',', has_header=True)
   #tpt.set_datafile_info(datafiles='/tmp/location_postal.csv', sep=',', has_header=True)
   #tpt.set_datafile_info(datafiles='/tmp/SearchAndRescue_3.csv', sep=',', has_header=True)
   #tpt.set_datafile_info(datafiles='/tmp/garages.csv', sep=',', has_header=True)
   #tpt.set_datafile_info(datafiles='/tmp/tpt_el_testdata22222.csv', sep=',', has_header=False)
   #tpt.set_datafile_info(datafiles='/common/SF_Cases_from_Feng_Dec31_for_upload.csv', sep=',', has_header=True)
   tpt.set_datafile_info(datafiles='/tmp/tpt_data_from_dt.csv', sep=',', has_header=False)
   tpt.set_sample_size(1000)
   #tpt.set_idx_columns(['uid', 'username'])
   #tpt.set_driver('pp_oap_seller_bi_test_t.BI_KPI_ONB_raw')
   tpt.set_driver('pp_oap_seller_bi_test_t.el_test_load_errorlimit_01')
   tpt.load()



def testExport():
   tpt = TPT()
   #export_sql_stmt = 'select * from pp_oap_seller_bi_test_t.el_wd_out'
   export_sql_stmt = 'sel * from pp_oap_seller_bi_t.ys_stevew_am_acct_2exclude_fnlbk'
   #export_sql_stmt = 'select * from dbc.tablesv'
   #export_sql_stmt = 'select * from pp_oap_seller_bi_test_t.el_stamp_test_data_2222_fbb'
   sep = ','
   tpt_export_data_file = '/tmp/tpt_data_from_dt.csv'
   tpt.set_export_datafile_info(sql_stmt=export_sql_stmt, sep=sep, tpt_export_data_file=tpt_export_data_file)
   tpt.export()


if __name__=='__main__':
   testLoad()
   #testExport()
