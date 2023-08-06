# copyright 2012-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.


from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubes.processing.testing import ProcessingTCMixin, ChainingTestMixin


class UsesExecutableHookTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(UsesExecutableHookTC, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            self.exe1eid = self.exeeid
            exe1 = cnx.entity_from_eid(self.exe1eid)
            self._add_iset_1(exe1)
            self._add_oset_1(exe1)
            exe2 = ce('Executable', name=u'e2')
            self.exe2eid = exe2.eid
            self._add_iset_2(exe2)
            self._add_oset_2(exe2)
            cnx.commit()

    def test_wiring_language(self):
        # test creation
        with self.admin_access.repo_cnx() as cnx:
            runchain = cnx.create_entity(
                'RunChain', uses_executable=(self.exe1eid, self.exe2eid))
            cnx.commit()
            self.assertEqual(
                len(self.runchain_wlang_def(runchain)['modules']), 2)
            # test edition
            cnx.execute('DELETE S uses_executable E WHERE S eid %(s)s, '
                        'E eid %(e)s', {'s': runchain.eid, 'e': self.exe1eid})
            cnx.commit()
            self.assertEqual(
                len(self.runchain_wlang_def(runchain)['modules']), 1)
            # test deletion
            cnx.execute('DELETE RunChain S WHERE S eid %(s)s',
                         {'s': runchain.eid})
            cnx.commit()


class ParameterOfHookTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(ParameterOfHookTC, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exeeid)
            ce = cnx.create_entity
            self._add_iset_1(exe)
            self._add_oset_1(exe)
            runchain = ce('RunChain', uses_executable=(exe,))
            self.runchaineid = runchain.eid
            cnx.commit()
            # check tests prerequisites
            fields = self.wlang_fields_by_module(
                self.runchain_wlang_def(runchain))
            self.assertEqual(len(fields), 1) # one exe
            self.assertEqual(len(fields[0][1]), 5) # 2 inputs, 3 outputs

    def test_input_parameter_of(self):
        '''Adding an input parameter to an executable should regenerate runchain's
        wiring language'''
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exeeid)
            exe.add_input(u'pnew', u'String')
            cnx.commit()
            runchain = cnx.entity_from_eid(self.runchaineid)
            fields = self.wlang_fields_by_module(
                self.runchain_wlang_def(runchain))
            self.assertEqual(len(fields), 1)
            self.assertEqual(len(fields[0][1]), 6)

    def test_output_parameter_of(self):
        '''Adding an output parameter to an executable should regenerate runchain's
        wiring language'''
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exeeid)
            exe.add_output(u'onew', u'String')
            cnx.commit()
            runchain = cnx.entity_from_eid(self.runchaineid)
            fields = self.wlang_fields_by_module(
                self.runchain_wlang_def(runchain))
            self.assertEqual(len(fields), 1)
            self.assertEqual(len(fields[0][1]), 6)


class InputParameterValueOrFromOutputRequiredTC(ChainingTestMixin, CubicWebTC):
    '''test hook part of the ParameterValue coherency checks
    -see also unittest_schema.py for constraint part-'''

    def test_value_required(self):
        'ParameterValue value is required when no link to an output is setup'
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            run1 = ce('Run', executable=self.exe1eid)
            with self.assertRaises(ValidationError) as cm:
                ce('ParameterValueFloat', param_def=self.idef1_feid,
                   value_of_run=run1)
                cnx.commit()
            self.assertExcMsg(cm, 'value is required for parameter "f"')

    def test_from_output_required(self):
        '''removing from_output relation is not possible when no value was
        specified'''
        with self.admin_access.repo_cnx() as cnx:
            pval = self.chaining_setup(cnx)
            with self.assertRaises(ValidationError) as cm:
                pval.cw_set(from_output=None)
                cnx.commit()
            self.assertExcMsg(cm, 'value is required for parameter "f"')

    def _file_pvalue(self, cnx, with_value=True):
        ce = cnx.create_entity
        exe = ce('Executable', name=u'e')
        pdef = exe.add_input(u'fp', u'File')
        cnx.commit()
        run = ce('Run', executable=exe)
        pval = self.new_file_pval(cnx, pdef, run, with_value=with_value)
        cnx.commit()
        return pval

    def test_file_value_required(self):
        with self.admin_access.repo_cnx() as cnx:
            pval = self._file_pvalue(cnx)
            with self.assertRaises(ValidationError) as ctm:
                pval.value.cw_delete()
                cnx.commit()
            self.assertExcMsg(ctm, 'value is required for parameter "fp"')

    def _file_odef_setup(self, cnx):
        ce = cnx.create_entity
        exe1 = ce('Executable', name=u'e1')
        odef = ce('ParameterDefinition',
                  name=u'fo',
                  value_type=u'File',
                  param_type=u'output',
                  parameter_of=exe1)
        cnx.commit()
        return ce('Run', executable=exe1), odef

    def test_file_value_from_output_required(self):
        with self.admin_access.repo_cnx() as cnx:
            run, odef = self._file_odef_setup(cnx)
            pval = self._file_pvalue(cnx, with_value=False)
            pval.cw_set(from_run=run, from_output=odef)
            cnx.commit()
            with self.assertRaises(ValidationError) as cm:
                pval.cw_set(from_output=None)
                cnx.commit()
            self.assertExcMsg(cm, 'value is required for parameter "fp"')


class RunChainingTC(ChainingTestMixin, CubicWebTC):

    def test_output_copy(self):
        '''When a Run receives an output value linked to a input value,
        the value is copied from the output into the input.
        '''
        with self.admin_access.repo_cnx() as cnx:
            pval = self.chaining_setup(cnx)
            obj = cnx.create_entity(
                'ParameterValueFloat', value=3.7,
                param_def=pval.from_output, value_of_run=pval.from_run[0])
            cnx.commit()
            pval.cw_clear_all_caches()
            self.assertEqual(pval.value, obj.value)


class RunChainRunsGenerationHooksTC(CubicWebTC):

    def test_new_linked_wiring(self):
        self.skipTest('to be implemented soon')

    def test_updated_wiring(self):
        self.skipTest('to be implemented soon')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
