"""cubicweb-datacat test utilities"""

from cubicweb.devtools.testlib import CubicWebTC

from utils import create_file


class DataProcessWorkflowHooksTC(CubicWebTC):

    def _setup_and_start_dataprocess(self, cnx, process_etype, scriptcode):
        inputfile = create_file(cnx, 'data')
        script = cnx.create_entity('Script',
                                   name=u'%s script' % process_etype)
        create_file(cnx, scriptcode, reverse_implemented_by=script.eid)
        with cnx.security_enabled(write=False):
            process = cnx.create_entity(process_etype,
                                        process_script=script)
            cnx.commit()
        process.cw_clear_all_caches()
        iprocess = process.cw_adapt_to('IDataProcess')
        self.assertEqual(process.in_state[0].name,
                         iprocess.state_name('initialized'))
        process.cw_set(process_input_file=inputfile)
        cnx.commit()
        process.cw_clear_all_caches()
        return process

    def test_data_process_autostart(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('Script', name=u'v')
            create_file(cnx, '1/0', reverse_implemented_by=script)
            with cnx.security_enabled(write=False):
                process = cnx.create_entity('DataValidationProcess',
                                            process_script=script)
                cnx.commit()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_initialized')
            inputfile = create_file(cnx, 'data')
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_error')

    def test_data_process(self):
        with self.admin_access.repo_cnx() as cnx:
            for ptype in ('transformation', 'validation'):
                etype = 'Data' + ptype.capitalize() + 'Process'
                process = self._setup_and_start_dataprocess(cnx, etype, 'pass')
                self.assertEqual(process.in_state[0].name,
                                 'wfs_dataprocess_completed')
                process.cw_delete()
                cnx.commit()
                process = self._setup_and_start_dataprocess(cnx, etype, '1/0')
                self.assertEqual(process.in_state[0].name,
                                 'wfs_dataprocess_error')

    def test_data_process_output(self):
        with self.admin_access.repo_cnx() as cnx:
            self._setup_and_start_dataprocess(
                cnx, 'DataTransformationProcess',
                open(self.datapath('cat.py')).read())
            rset = cnx.execute(
                'Any X WHERE EXISTS(X produced_by S)')
            self.assertEqual(len(rset), 1)
            stdout = rset.get_entity(0, 0)
            self.assertEqual(stdout.read(), 'data\n')

    def test_data_validation_process_validated_by(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('Script', name=u'v')
            create_file(cnx, 'pass', reverse_implemented_by=script)
            with cnx.security_enabled(write=False):
                process = cnx.create_entity('DataValidationProcess',
                                            process_script=script)
                cnx.commit()
            inputfile = create_file(cnx, 'data')
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_completed')
            validated = cnx.find('File', validated_by=process).one()
            self.assertEqual(validated, inputfile)

    def test_data_process_dependency(self):
        """Check data processes dependency"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = cnx.create_entity('Script', name=u'v')
            create_file(cnx, 'pass', reverse_implemented_by=vscript)
            with cnx.security_enabled(write=False):
                vprocess = cnx.create_entity('DataValidationProcess',
                                             process_script=vscript)
                cnx.commit()
            tscript = cnx.create_entity('Script', name=u't')
            create_file(cnx,
                        ('import sys;'
                         'sys.stdout.write(open(sys.argv[1]).read())'),
                        reverse_implemented_by=tscript)
            with cnx.security_enabled(write=False):
                tprocess = cnx.create_entity('DataTransformationProcess',
                                             process_depends_on=vprocess,
                                             process_script=tscript)
                cnx.commit()
            inputfile = create_file(cnx, 'data')
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_completed'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_completed')
            rset = cnx.find('File', produced_by=tprocess)
            self.assertEqual(len(rset), 1, rset)
            output = rset.one()
            self.assertEqual(output.read(), inputfile.read())

    def test_data_process_dependency_validation_error(self):
        """Check data processes dependency: validation process error"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = cnx.create_entity('Script', name=u'v')
            create_file(cnx, '1/0', reverse_implemented_by=vscript)
            with cnx.security_enabled(write=False):
                vprocess = cnx.create_entity('DataValidationProcess',
                                             process_script=vscript)
                cnx.commit()
            tscript = cnx.create_entity('Script', name=u't')
            create_file(cnx, 'import sys; print open(sys.argv[1]).read()',
                        reverse_implemented_by=tscript)
            with cnx.security_enabled(write=False):
                tprocess = cnx.create_entity('DataTransformationProcess',
                                             process_depends_on=vprocess,
                                             process_script=tscript)
                cnx.commit()
            inputfile = create_file(cnx, 'data')
            # Triggers "start" transition.
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_error'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_initialized')


if __name__ == '__main__':
    import unittest
    unittest.main()
