# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"Unittests for security of processing cube"

from cubicweb import ValidationError, Unauthorized
from cubicweb.devtools.testlib import CubicWebTC


class RunExecutableTraceabilityTC(CubicWebTC):
    """Check the security model which should ensure traceability of Run with
    respect to Executable.

    Create an Executable with ParameterDefinitions and an associated Run
    with a ParameterValues. Check various actions as a regular user (owner)
    and a manager.
    """

    def setup_database(self):
        """Create an Executation with a ParameterDefinition and an associated
        Run with a ParameterValue, as non-manager"""
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, u'toto')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            exe = cnx.create_entity('Executable', name=u'exe')
            i1 = cnx.create_entity('ParameterDefinition', value_type=u'Float',
                                   param_type=u'input',
                                   name=u'i1', parameter_of=exe)
            i2 = cnx.create_entity('ParameterDefinition', value_type=u'Float',
                                   param_type=u'input',
                                   name=u'i2', parameter_of=exe)
            cnx.commit()
            with cnx.allow_all_hooks_but('processing.test'):
                run = cnx.create_entity('Run', executable=exe)
                run[i1.name] = 3.2
                run[i2.name] = 4.5
                cnx.commit()
            self.assertInState(run, 'wfs_run_ready')
            self.i1_eid = i1.eid
            self.i2_eid = i2.eid
            self.i1v_eid = run.ivalue_entity(i1.name).eid
            self.i2v_eid = run.ivalue_entity(i2.name).eid
            self.exe_eid = exe.eid
            self.run_eid = run.eid

    def assertExcMsg(self, ctm, expected):
        if not str(ctm.exception).endswith(expected):
           self.fail('did not get error %r but %s' % (expected, ctm.exception))

    def test_exe_modification(self):
        """Cannot modify Executable associated to a Run"""
        with self.new_access('toto').client_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exe_eid)
            with self.assertRaises(Unauthorized):
                exe.cw_set(name=u'boom')
                cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exe_eid)
            exe.cw_set(name=u'moob')
            cnx.commit()

    def change_executable(self, cnx):
        e1 = cnx.create_entity('Executable', name=u'exe1')
        cnx.execute("SET R executable E WHERE R is Run, R eid %(r)s, "
                    "E eid %(e)s", {'e': e1.eid, 'r': self.run_eid})
        cnx.commit()

    def test_exe_change_relation(self):
        """Cannot change `Run executable Executable` relation"""
        with self.new_access('toto').client_cnx() as cnx:
            with self.assertRaises(Unauthorized):
                self.change_executable(cnx)
        with self.admin_access.repo_cnx() as cnx:
            self.change_executable(cnx)

    def delete_executable(self, cnx):
        cnx.execute("DELETE Executable E WHERE E eid %(e)s",
                    {'e': self.exe_eid})
        cnx.commit()

    def test_exe_delete(self):
        """Cannot delete Executable associated to a Run"""
        with self.new_access('toto').client_cnx() as cnx:
            with self.assertRaises(ValidationError):
                self.delete_executable(cnx)

    def test_pdef_add(self):
        """Cannot add a ParameterDefinition to an Executable used in a Run"""
        with self.admin_access.repo_cnx() as cnx:
            exe = cnx.entity_from_eid(self.exe_eid)
            with self.assertRaises(ValidationError) as ctm:
                exe.add_input(name=u'p', value_type=u'Float')
                cnx.commit()
            self.assertExcMsg(ctm, "can't modify parameters of an executable "
                              "which is already used in a run")

    def remove_pdef(self, cnx):
        rql = "DELETE ParameterDefinition P WHERE P eid %(eid)s"
        cnx.execute(rql, {"eid": self.i1_eid})
        cnx.commit()

    def test_cannot_remove_pdef_if_pvals_attached(self):
        """Cannot delete a ParameterDefinition if a ParameterValue
        uses this definition"""
        # even manager is not allowed
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(ValidationError):
                self.remove_pdef(cnx)

    def test_pdef_remove(self):
        """Cannot delete a ParameterDefinition of an Executable used in a
        Run"""
        with self.new_access('toto').client_cnx() as cnx:
            with self.assertRaises(Unauthorized):
                self.remove_pdef(cnx)
        # manager is allowed
        with self.admin_access.repo_cnx() as cnx:
            self.delete_pval(cnx)
            self.remove_pdef(cnx)

    def update_pdef(self, cnx):
        i1 = cnx.entity_from_eid(self.i1_eid)
        i1.cw_set(value_type=u'Int')
        cnx.commit()

    def test_pdef_update(self):
        """Cannot modify a ParameterDefinition of an Executable used in a
        Run"""
        with self.new_access('toto').client_cnx() as cnx:
            with self.assertRaises(Unauthorized):
                self.update_pdef(cnx)
        # manager is allowed
        with self.admin_access.repo_cnx() as cnx:
            self.update_pdef(cnx)

    def remove_parameter_of_relation(self, cnx):
        rql = ("DELETE I parameter_of E WHERE E is Executable, E eid %(e)s, "
               "I is ParameterDefinition, I eid %(i)s")
        cnx.execute(rql, {"e": self.exe_eid, "i": self.i1_eid})
        cnx.commit()

    def test_parameter_of_remove(self):
        """Cannot remove `ParameterDefinition parameter_of Executable`
        relation"""
        with self.new_access('toto').repo_cnx() as cnx:
            # cardinality is 1 but we want to test security not cardinality
            cnx.disable_hook_categories('integrity')
            with self.assertRaises(Unauthorized):
                self.remove_parameter_of_relation(cnx)
        # manager is allowed
        with self.admin_access.repo_cnx() as cnx:
            self.delete_pval(cnx)
            cnx.disable_hook_categories('integrity')
            self.remove_parameter_of_relation(cnx)

    def delete_pval(self, cnx):
        cnx.execute("DELETE ParameterValueFloat V WHERE V eid %(v)s",
                    {"v": self.i1v_eid})
        cnx.commit()

    def test_pval_delete(self):
        """Cannot delete a ParameterValue"""
        with self.new_access('toto').client_cnx() as cnx:
            with self.assertRaises(Unauthorized):
                self.delete_pval(cnx)
        with self.admin_access.repo_cnx() as cnx:
            self.delete_pval(cnx)

    def change_param_def(self, cnx):
        cnx.execute("SET V1 param_def D2, V2 param_def D1 WHERE "
                    "D1 is ParameterDefinition, D2 is ParameterDefinition, "
                    "V1 eid %(v1)s, D1 eid %(d1)s, V2 eid %(v2)s, D2 eid %(d2)s",
                    {"v1": self.i1v_eid, "d1": self.i1_eid,
                     "v2": self.i2v_eid, "d2": self.i2_eid})
        cnx.commit()

    def test_param_def_change(self):
        """Cannot change the `ParameterValue param_def ParameterDefinition`
        relation"""
        with self.new_access('toto').client_cnx() as cnx:
            with self.assertRaises(Unauthorized):
                self.change_param_def(cnx)
        with self.admin_access.repo_cnx() as cnx:
            self.change_param_def(cnx)

    def test_pdef_update_no_pval(self):
        """Cannot change a ParameterDefinition, even if there's no
        ParameterValue (though the Run is still linked)"""
        # first drop the ParameterValue (as admin)
        with self.admin_access.repo_cnx() as cnx:
            self.delete_pval(cnx)
        with self.new_access('toto').client_cnx() as cnx:
            i1 = cnx.entity_from_eid(self.i1_eid)
            # update ParameterDefinition
            with self.assertRaises(Unauthorized):
                i1.cw_set(value_type=u'Int')
                cnx.commit()
            # drop the parameter_of relation
            with self.assertRaises(Unauthorized):
                cnx.execute("DELETE I parameter_of E WHERE E is Executable, "
                            "E eid %(e)s, I is ParameterDefinition, I eid %(i)s",
                            {'e': self.exe_eid, 'i': self.i1_eid})
                cnx.commit()
            # delete it
            with self.assertRaises(Unauthorized):
                cnx.execute("DELETE ParameterDefinition D WHERE D eid %(d)s",
                            {"d": self.i1_eid})
                cnx.commit()

    def assertInState(self, entity, statename):
        entity.cw_clear_all_caches()
        self.assertEqual(entity.cw_adapt_to('IWorkflowable').state, statename)

    def test_modify_pval_wf(self):
        """Cannot modify ParameterValue if Run is not in state wfs_run_setup or
        wfs_run_ready"""
        with self.new_access(u'toto').repo_cnx() as cnx:
            run = cnx.entity_from_eid(self.run_eid)
            i1v = cnx.entity_from_eid(self.i1v_eid)
            i1v.cw_set(value=4.5)
            cnx.commit()

            with cnx.allow_all_hooks_but('processing.test'):
                run.cw_adapt_to('IWorkflowable').fire_transition('wft_run_queue')
                cnx.commit()

            self.assertInState(run, 'wfs_run_waiting')
            with self.assertRaises(Unauthorized):
                i1v.cw_set(value=-2.3)
                cnx.commit()

        # need manager permissions to fire run transition
        with self.admin_access.repo_cnx() as cnx:
            run_ = cnx.entity_from_eid(self.run_eid)
            with cnx.allow_all_hooks_but('processing.test'):
                run_.cw_adapt_to('IWorkflowable').fire_transition('wft_run_run')
                cnx.commit()
            self.assertInState(run_, 'wfs_run_running')

        with self.new_access('toto').client_cnx() as cnx:
            i1v = cnx.entity_from_eid(self.i1v_eid)
            with self.assertRaises(Unauthorized):
                i1v.cw_set(value=0)
                cnx.commit()


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
