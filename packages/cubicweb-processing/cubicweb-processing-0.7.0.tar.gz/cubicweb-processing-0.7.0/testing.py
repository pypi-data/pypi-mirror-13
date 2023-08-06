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
"""tools helping cubicweb-processing client to test their code"""

from random import random, randint, choice
from json import loads, dumps

from logilab.common.shellutils import generate_password

from cubicweb import Binary
from cubicweb.devtools.fill import ValueGenerator


class MyValueGenerator(ValueGenerator):

    def generate_Any_json(self, entity, index):
        return unicode(dumps({'modules': ()}))

    def generate_Executable_python_code(self, entity, index):
        return u'1'


def generate_param_value(value_type, req):
    if value_type == 'Int':
        return randint(-1000, 1000)
    if value_type == 'Float':
        return random() * 1000
    if value_type == 'String':
        return unicode(generate_password())
    if value_type == 'File':
        data_name = u'toto.' + choice([u'py', u'txt', u'xls', u'dat'])
        return req.create_entity('File', data_name=data_name,
                                 data=Binary(generate_password()))

def generate_io(tc, cnx):
    with cnx.allow_all_hooks_but('integrity', 'processing.test'):
        for exe in cnx.execute('Executable X').entities():
            for vtype in (u'Int', u'Float', u'String', u'File'):
                exe.add_input('i'+vtype, vtype)
                exe.add_output('o'+vtype, vtype)
            for run in exe.reverse_executable:
                for vtype in (u'Int', u'Float', u'String', u'File'):
                    run['i'+vtype] = generate_param_value(vtype, cnx)


class ProcessingTCMixin(object):

    def setup_database(self):
        super(ProcessingTCMixin, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            self.exeeid = cnx.create_entity(
                    'Executable', name=u'some executable').eid
            cnx.commit()

    def assertExcMsg(self, ctm, expected):
        if not str(ctm.exception).endswith(expected):
           self.fail('did not get error %r but %s' % (expected, ctm.exception))

    def new_run(self, cnx, **kwargs):
        return cnx.create_entity('Run', **kwargs)

    def new_file_pval(self, cnx, pdef, run, with_value=True):
        ce = cnx.create_entity
        pval = ce('ParameterValueFile', param_def=pdef, value_of_run=run)
        if with_value:
            ce('File', data_name=u'file.txt', data=Binary("content"),
               data_format=u"text/plain", reverse_value_file=pval)
        return pval

    def runchain_wlang_def(self, runchain):
        if runchain.wlang:
            runchain.wlang[0].cw_clear_all_caches()
            return loads(runchain.wlang[0].json)

    def wlang_fields_by_module(self, wlang):
        fields = []
        for mod in wlang['modules']:
            fields.append((mod['name'],
                           sorted([(f['inputParams']['name'], f['type'])
                                   for f in mod['container']['fields']])))
        return fields

    def _add_iset_1(self, exe):
        exe.add_input(u'i11', u'Float')
        exe.add_input(u'i12', u'String')

    def _add_oset_1(self, exe):
        exe.add_output(u'o11', u'Float')
        exe.add_output(u'o12', u'String')
        exe.add_output(u'o13', u'Float')

    def _add_iset_2(self, exe):
        exe.add_input(u'i21', u'Float')
        exe.add_input(u'i22', u'Float')
        exe.add_input(u'i23', u'String')

    def _add_oset_2(self, exe):
        exe.add_output(u'o21', u'String')
        exe.add_output(u'o22', u'Float')


class ChainingTestMixin(ProcessingTCMixin):

    def setup_database(self):
        super(ChainingTestMixin, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            exe0 = ce('Executable', name=u'e0')
            self.exe0eid = exe0.eid
            self.odef0_feid = exe0.add_output(u'f', u'Float').eid
            self.odef0_seid = exe0.add_output(u's', u'String').eid
            exe1 = ce('Executable', name=u'e1')
            self.exe1eid = exe1.eid
            self.idef1_feid = exe1.add_input(u'f', u'Float').eid
            cnx.commit()

    def chaining_setup(self, cnx):
        ce = cnx.create_entity
        run0 = ce('Run', executable=self.exe0eid)
        run1 = ce('Run', executable=self.exe1eid)
        pval = ce('ParameterValueFloat',
                  param_def=self.idef1_feid,
                  value_of_run=run1,
                  from_run=run0,
                  from_output=self.odef0_feid)
        cnx.commit()
        return pval


class RunChainTCMixin(ProcessingTCMixin):

    def setup_database(self):
        super(RunChainTCMixin, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            ce = cnx.create_entity
            # add a new run with files
            exe0 = ce('Executable', name=u'e0')
            self.exe0eid = exe0.eid
            idef1 = exe0.add_input(u'i1', u'File')
            idef2 = exe0.add_input(u'i2', u'Float')
            odef1 = exe0.add_output(u'o1', u'File')
            odef2 = exe0.add_output(u'o2', u'Float')
            cnx.commit()
            run = ce('Run', executable=exe0)
            pv1 = self.new_file_pval(cnx, idef1, run, with_value=True)
            idef2.create_value(1., run)
            cnx.commit()
            self.exe1eid = self.exeeid
            exe1 = cnx.entity_from_eid(self.exe1eid)
            self._add_iset_1(exe1)
            self._add_oset_1(exe1)
            exe2 = ce('Executable', name=u'e2')
            self.exe2eid = exe2.eid
            self._add_iset_2(exe2)
            self._add_oset_2(exe2)
            runchain = ce('RunChain', uses_executable=(exe0, exe1, exe2))
            self.runchaineid = runchain.eid
            cnx.commit()
            exe = cnx.entity_from_eid(self.exeeid)
            descr = {
                u'modules': [
                {u'config': {u'position': [167, 71]},
                 u'name': exe.dc_title(),
                 u'eid': self.exeeid,
                 u'value': {u'o11': '[wired]',
                            u'o12': u'',
                            # do not rely on '[wired]' value, also test None:
                            u'o13': None,
                            u'i11': 1.1,
                            u'i12': u'1.2'}},
                {u'config': {u'position': [634, 161]},
                 u'name': exe2.dc_title(),
                 u'eid': self.exe2eid,
                 u'value': {u'o21': u'',
                            u'o22': u'',
                            u'i21': '[wired]',
                            u'i22': '[wired]',
                            u'i23': u'i23 value'}},
                {u'config': {u'position': [2, 40]},
                 u'name': exe0.dc_title(),
                 u'eid': self.exe0eid,
                 u'value': {u'o1': u'',
                            u'o2': u'',
                            u'i1':  u'%s' % pv1.value_file[0].eid,
                            u'i2': u'1.0'}},],
                u'properties': None,
                u'wires': [{u'src': {u'moduleId': 0, u'terminal': u'o11'},
                            u'tgt': {u'moduleId': 1, u'terminal': u'i21'}},
                           {u'src': {u'moduleId': 0, u'terminal': u'o13'},
                            u'tgt': {u'moduleId': 1, u'terminal': u'i22'}}]
            }
            ce('Wiring', name=u'test', json=unicode(dumps(descr)),
               reverse_wiring=runchain, language=runchain.wlang[0])
            cnx.commit()
