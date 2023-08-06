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
"Unittests for the schema of processing cube"

from contextlib import contextmanager
from json import dumps

from cubicweb import ValidationError, Unauthorized, Binary
from cubicweb.schema import ERQLExpression
from cubicweb.devtools.testlib import CubicWebTC

from cubes.processing.testing import ProcessingTCMixin, ChainingTestMixin


class ParameterDefinitionSchemaTC(ProcessingTCMixin, CubicWebTC):

    def test_pdef_name_validity(self):
        'check parameter definition name restrictions'
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(ValidationError) as ctm:
                exe = cnx.entity_from_eid(self.exeeid)
                exe.add_input(name=u'p 1', value_type=u'Float')
            self.assertExcMsg(ctm, ("doesn't match the '^[a-zA-Z0-9_]+$' "
                                    "regular expression"))

    def test_pdef_unique(self):
        'same parameter definition name for same executable is invalid'
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exeeid)
            i1 = exe.add_input(name=u'i1', value_type=u'Float')
            with self.assertRaises(ValidationError) as ctm:
                exe.add_input(name=i1.name, value_type=i1.value_type)
                cnx.commit()
            self.assertExcMsg(ctm, 'parameter name is already used')


class ParameterValueSchemaTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(ParameterValueSchemaTC, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exeeid)
            self.idefeid = exe.add_input(u'p', u'Float').eid
            cnx.commit()

    def test_wrong_pval_type(self):
        'cannot assign a wrong type ParameterValue'
        with self.admin_access.repo_cnx() as cnx:
            run = cnx.create_entity('Run', executable=self.exeeid)
            with self.assertRaises(ValidationError):
                cnx.create_entity('ParameterValueString',
                                  param_def=self.idefeid,
                                  value=u'coucou',
                                  value_of_run=run)
                cnx.commit()

    def set_owner(self, user, *entities):
        for entity in entities:
            if isinstance(entity, int):
                entity = user._cw.entity_from_eid(entity)
            entity.cw_set(owned_by=user)

    def test_pval_perms(self):
        'cannot modify a ParameterValue if linked Run cannot be modified'
        # we use a non manager user to test: set him as owner of objects
        with self.admin_access.repo_cnx() as cnx:
            self.set_owner(self.create_user(cnx, 'user'),
                           self.exeeid, self.idefeid)
            cnx.commit()
        # actual test
        with self.new_access('user').repo_cnx() as cnx:
            # - add a Run with a parameter value
            idef = cnx.entity_from_eid(self.idefeid)
            with cnx.allow_all_hooks_but('processing.test'):
                run = cnx.create_entity('Run', executable=self.exeeid)
                run[idef.name] = 1.
                cnx.commit()
            # - check it can be modified for now
            run[idef.name] = 2.
            cnx.commit()
            # - make the run not modifiable
            with self.temporary_permissions((self.schema['Run'],
                                             dict(update=()))):
                with self.assertRaises(Unauthorized):
                    run[idef.name] = 4.
                    cnx.commit()


class ChainingSetupTC(ChainingTestMixin, CubicWebTC):

    def assertConstraintCrashes(self, cnx, msg):
        with self.assertRaises(ValidationError) as cm:
            cnx.commit()
        self.assertTrue(str(cm.exception).endswith(msg), str(cm.exception))

    def test_from_run_same_type(self):
        '''input parameter cannot be copied from a run without an output
        parameter of the same type'''
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            run_no_param = ce('Run', executable=self.exeeid)
            run1 = ce('Run', executable=self.exe1eid)
            ce('ParameterValueFloat', param_def=self.idef1_feid, value=1.,
               value_of_run=run1, from_run=run_no_param)
            self.assertConstraintCrashes(
                cnx, 'specified run has no output parameter of the right type')

    def test_from_output_same_type(self):
        '''An input parameter definition cannot be copied from an output
        parameter with a different type'''
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            run0 = ce('Run', executable=self.exe0eid)
            run1 = ce('Run', executable=self.exe1eid)
            ce('ParameterValueFloat', param_def=self.idef1_feid, value=1.,
               value_of_run=run1, from_run=run0, from_output=self.odef0_seid)
            self.assertConstraintCrashes(
                cnx, 'copied output parameter has wrong value type')

    def test_from_output_same_run(self):
        '''An input parameter definition cannot be copied from an output
        parameter not related to the chained run'''
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            exe = cnx.entity_from_eid(self.exeeid)
            o_param_other_f = exe.add_output(u'f', u'Float')
            cnx.commit()
            run_other = ce('Run', executable=self.exeeid)
            run0 = ce('Run', executable=self.exe0eid)
            cnx.commit()
            run1 = ce('Run', executable=self.exe1eid)
            pval1_f = ce('ParameterValueFloat', param_def=self.idef1_feid, value=1.,
                         value_of_run=run1, from_run=run0,
                         from_output=o_param_other_f)
            self.assertConstraintCrashes(
                cnx, 'copied output parameter is unrelated to source run')


class RunSchemaTC(ProcessingTCMixin, CubicWebTC):

    def test_input_values_pdef_exists_ok(self):
        'can add parameter if it corresponds to a param def of the executable'
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            exe = cnx.entity_from_eid(self.exeeid)
            p = exe.add_input(u'p', u'Float')
            cnx.commit()
            run = ce('Run', executable=exe)
            run[p.name] = 1.
            cnx.commit()

    def test_input_values_pdef_exists_error(self):
        '''cannot add parameter value which does not correspond to a parameter
        definition of the executable'''
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            exe2 = ce('Executable', name=u'e2')
            pexe2 = exe2.add_input(u'p', u'Float')
            cnx.commit()
            with self.assertRaises(ValidationError) as ctm:
                run = ce('Run', executable=self.exeeid)
                ce('ParameterValueFloat', param_def=pexe2, value=1.,
                   value_of_run=run)
                cnx.commit()
            cnx.rollback()
            self.assertExcMsg(
                ctm, 'cannot find such a parameter for this executable')

    def test_executable_constraint(self):
        '''cannot link run to executable with param defs without defining
        corresponding param values'''
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            exe = cnx.entity_from_eid(self.exeeid)
            exe.add_input(u'p', u'Float')
            cnx.commit()
            with self.assertRaises(ValidationError) as ctm:
                ce('Run', executable=self.exeeid)
                cnx.commit()
            cnx.rollback()
            self.assertExcMsg(ctm, 'missing input parameter values')

    def test_input_values_unique(self):
        'cannot add 2 input param values for the same definition on same run'
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            p = ce('ParameterDefinition',
                   name=u'p',
                   value_type=u'Float',
                   param_type=u'input',
                   parameter_of=self.exeeid)
            cnx.commit()
            run = ce('Run', executable=self.exeeid)
            ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
            cnx.commit()
            with self.assertRaises(ValidationError) as ctm:
                ce('ParameterValueFloat', param_def=p, value=1.,
                   value_of_run=run)
                cnx.commit()
            self.assertExcMsg(ctm, 'this parameter has several values')

    def test_output_values_odef_exists_ok(self):
        '''can add output parameter value if it corresponds to an output
        parameter definition of the executable'''
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            p = ce('ParameterDefinition',
                   name=u'p',
                   value_type=u'Float',
                   param_type=u'output',
                   parameter_of=self.exeeid)
            cnx.commit()
            run = ce('Run', executable=self.exeeid)
            ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
            cnx.commit()

    def test_output_values_odef_exists_error(self):
        '''cannot add an output parameter value which does not correspond to an
        output parameter definition of the executable'''
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            exe2 = ce('Executable', name=u'e2')
            pexe2 = ce('ParameterDefinition',
                       name=u'p',
                       value_type=u'Float',
                       param_type=u'output',
                       parameter_of=exe2)
            cnx.commit()
            with self.assertRaises(ValidationError) as ctm:
                run = ce('Run', executable=self.exeeid)
                ce('ParameterValueFloat', param_def=pexe2, value=1.,
                   value_of_run=run)
                cnx.commit()
            cnx.rollback()
            self.assertExcMsg(
                ctm, 'cannot find such a parameter for this executable')

    def test_output_values_unique(self):
        'cannot add 2 output param values for the same definition on same run'
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            p = ce('ParameterDefinition',
                   name=u'p',
                   value_type=u'Float',
                   param_type=u'output',
                   parameter_of=self.exeeid)
            cnx.commit()
            run = ce('Run', executable=self.exeeid)
            ce('ParameterValueFloat', param_def=p, value=1., value_of_run=run)
            cnx.commit()
            with self.assertRaises(ValidationError) as ctm:
                ce('ParameterValueFloat', param_def=p, value=1.,
                   value_of_run=run)
                cnx.commit()
            self.assertExcMsg(ctm, 'this parameter has several values')


class FileValueFunctionalTC(ProcessingTCMixin, CubicWebTC):

    def setup_database(self):
        super(FileValueFunctionalTC, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exeeid)
            # data setup : executable and parameters
            pdef1 = exe.add_input(u'i1', u'File')
            pdef2 = exe.add_input(u'i2', u'Float')
            cnx.commit()
            # data setup : run and parameter values
            ce = cnx.create_entity
            run = ce('Run', executable=exe)
            self.runeid = run.eid
            pv1 = self.new_file_pval(cnx, pdef1, run, with_value=True)
            self.pv1eid = pv1.eid
            self.fvaleid = pv1.value_file[0].eid
            self.pv2eid = ce('ParameterValueFloat', value=1., param_def=pdef2,
                             value_of_run=run).eid
            cnx.commit()

    def assertExists(self, cnx, eid, false_true=True):
        rql = 'Any X WHERE X eid %(x)s'
        self.assertEqual(cnx.execute(rql, dict(x=eid)).rowcount,
                         int(false_true))

    def assertNotExists(self, cnx, eid):
        self.assertExists(cnx, eid, false_true=False)

    def test_remove_input_values(self):
        '''Parameter values must be deleted as soon as the Run is.
        File parameters are special in that we authorize sharing them between
        Run instances, but removing the only Run linked to a File value must
        remove it too.'''
        with self.admin_access.repo_cnx() as cnx:
            cnx.entity_from_eid(self.runeid).cw_delete()
            cnx.commit()
            self.assertNotExists(cnx, self.pv1eid)
            self.assertNotExists(cnx, self.pv2eid)
            self.assertNotExists(cnx, self.fvaleid)

    def test_wiring_update(self):
        '''Updating the Wiring of a RunChain regenerates the Run instances.
        During this operation, we do not want the File instances linked to
        ParameterValueFile instances of the Run to be removed, but reused
        by the new Run if applicable.
        This functional (yet simple) test intends to demonstrate this.'''
        # create test data
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            runchain = ce('RunChain', uses_executable=self.exeeid)
            cnx.commit()
            json = (u'{"modules":[{"eid":%(exe)s,"value":{"i1":%(f)s, "i2":1.0}}],"wires":[]}'
                    % {'exe':self.exeeid, 'f':dumps(self.fvaleid)})
            ce('Wiring', json=json, reverse_wiring=runchain, language=runchain.wlang)
            cnx.commit()
            # record values before wiring update
            runchain.cw_clear_all_caches()
            old_run = runchain.has_runs[0]
            old_pval = old_run.ivalue_entity('i1')
            fval = old_pval.value_file[0]
            # dummy yet sufficient wiring update
            runchain.wiring[0].cw_set(json=json+u' ')
            cnx.commit()
            # check everything happened as expected
            runchain.cw_clear_all_caches()
            self.assertTrue(old_run.eid != runchain.has_runs[0].eid)
            self.assertTrue(old_pval.eid != runchain.has_runs[0].ivalue_entity('i1').eid)
            self.assertEqual(runchain.has_runs[0].ivalue_entity('i1').value_file[0].eid,
                             fval.eid)
            # remove one reference to the file, and check it still exists
            cnx.entity_from_eid(self.runeid).cw_delete()
            cnx.commit()
            self.assertExists(cnx, fval.eid)
            # remove the other and check it was removed
            runchain.cw_delete()
            cnx.commit()
            self.assertNotExists(cnx, fval.eid)


class ProcessingStudyTC(CubicWebTC):

    def test_runchain_run_in_same_study(self):
        with self.admin_access.repo_cnx() as cnx:
            study1 = cnx.create_entity('ProcessingStudy', name=u's')
            study2 = cnx.create_entity('ProcessingStudy', name=u'u')
            cnx.commit()
            exe = cnx.create_entity('Executable', name=u'e')
            run = cnx.create_entity('Run', executable=exe, in_study=study1)
            runchain = cnx.create_entity('RunChain')
            cnx.commit()
            yield self.check_in_study, runchain, run, study2
            # Unset has_runs, set in_study.
            runchain.cw_set(has_runs=None)
            cnx.commit()
            yield self.check_has_runs, runchain, run, study2
            yield self.check_run_in_study, runchain, run, study2

    def check_in_study(self, runchain, run, study):
        self.set_description('in_study')
        runchain.cw_set(has_runs=run)
        runchain._cw.commit()
        with self.assertRaises(ValidationError) as exc:
            runchain.cw_set(in_study=study)
            runchain._cw.commit()
        self.assertIn('in_study-subject', str(exc.exception))

    def check_has_runs(self, runchain, run, study):
        self.set_description('has_runs')
        runchain.cw_set(in_study=study)
        runchain._cw.commit()
        with self.assertRaises(ValidationError) as exc:
            runchain.cw_set(has_runs=run)
            runchain._cw.commit()
        self.assertIn('has_runs-subject', str(exc.exception))

    def check_run_in_study(self, runchain, run, study):
        self.set_description('run_in_study')
        runchain.cw_set(has_runs=run, in_study=run.in_study[0])
        runchain._cw.commit()
        with self.assertRaises(ValidationError) as exc:
            run.cw_set(in_study=study)
            run._cw.commit()
        self.assertIn('in_study-subject', str(exc.exception))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
