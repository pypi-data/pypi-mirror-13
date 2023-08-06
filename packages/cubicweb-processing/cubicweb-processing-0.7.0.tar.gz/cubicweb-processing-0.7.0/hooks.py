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
"""cubicweb-processing specific hooks and operations"""


from cubicweb import ValidationError
from cubicweb.predicates import (is_instance, has_related_entities,
                                 on_fire_transition)
from cubicweb.server.hook import (Hook, Operation, LateOperation,
                                  DataOperationMixIn,
                                  match_rtype)


class RunChainCreation(Hook):
    __regid__ = 'processing.runchain_creation'
    __select__ = Hook.__select__ & is_instance('RunChain')
    events = ('before_add_entity',)

    def __call__(self):
        runchain = self.entity
        if 'name' not in runchain.cw_edited:
            runchain.cw_edited['name'] = u'<unnamed runchain %s>' % runchain.eid


class WiringLanguageOperation(DataOperationMixIn, Operation):

    def precommit_event(self):
        pendingeids = self.cnx.transaction_data.get('pendingeids', ())
        for st in self.get_data():
            if st.eid in pendingeids:
                continue # do not update wlang of studies being deleted
            kwargs = dict(name=st.wlang_name, json=st.wiring_language())
            if st.wlang:
                st.wlang[0].cw_set(**kwargs)
            else:
                self.cnx.create_entity('WiringLanguage', reverse_wlang=st,
                                           **kwargs)


class _WiringLanguageRegenerationRtypeHook(Hook):
    __abstract__ = True
    events = ('after_add_relation', 'after_delete_relation')

    @property
    def runchain(self):
        raise NotImplementedError

    def __call__(self):
        runchain = self.runchain
        if runchain is not None:
            WiringLanguageOperation.get_instance(self._cw).add_data(runchain)


class UsesExecutableHook(_WiringLanguageRegenerationRtypeHook):
    __regid__ = 'processing.uses_executable'
    __select__ = match_rtype('uses_executable',)

    @property
    def runchain(self):
        return self._cw.entity_from_eid(self.eidfrom)


class ParameterOfHook(_WiringLanguageRegenerationRtypeHook):
    __regid__ = 'processing.parameter_of'
    __select__ = match_rtype('parameter_of',)

    @property
    def runchain(self):
        exe = self._cw.entity_from_eid(self.eidto)
        if exe.reverse_uses_executable:
            return exe.reverse_uses_executable[0]


class InputParameterValueOrFromOutputRequiredOp(DataOperationMixIn, Operation):

    def precommit_event(self):
        pendingeids = self.cnx.transaction_data.get('pendingeids', ())
        for pval in self.get_data():
            if pval.eid in pendingeids:
                continue # ignore parameter values being deleted
            if pval.value is None and not pval.from_output:
                msg = self.cnx._('value is required for parameter "%s"')
                raise ValidationError(pval.eid, {'json': msg % pval.pname})


class InputParameterValueAddUpdateHook(Hook):
    __regid__ = 'processing.ival_add_update'
    __select__ = Hook.__select__ & is_instance(
        'ParameterValueFloat', 'ParameterValueInt', 'ParameterValueString')
    events = ('after_add_entity', 'after_update_entity')

    def __call__(self):
        ival = self.entity
        if ival.pdef.param_type == 'input':
            InputParameterValueOrFromOutputRequiredOp.get_instance(
                self._cw).add_data(ival)


class FromOutputDeleteHook(Hook):
    __regid__ = 'processing.from_output_delete'
    __select__ = match_rtype('from_output',)
    events = ('after_delete_relation',)

    def __call__(self):
        pval = self._cw.entity_from_eid(self.eidfrom)
        InputParameterValueOrFromOutputRequiredOp.get_instance(
            self._cw).add_data(pval)


class RemoveValueFileIfLastReferenceOp(DataOperationMixIn, Operation):

    def precommit_event(self):
        pendingeids = self.cnx.transaction_data.get('pendingeids', ())
        for fval in self.get_data():
            if fval.eid in pendingeids:
                continue
            fval.cw_clear_all_caches()
            if not fval.reverse_value_file:
                fval.cw_delete()


class ValueFileDeleteHook(Hook):
    __regid__ = 'processing.value_file_delete'
    __select__ = match_rtype('value_file',)
    events = ('after_delete_relation',)

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        # selector does not guarantee it is an input value:
        # it could be an output too!
        if entity.ptype == 'input':
            InputParameterValueOrFromOutputRequiredOp.get_instance(
                self._cw).add_data(entity)
            fval = self._cw.entity_from_eid(self.eidto)
            RemoveValueFileIfLastReferenceOp.get_instance(
                self._cw).add_data(fval)


class RunChainWiringGenOperation(DataOperationMixIn, Operation):
    '''
    Operation that regenerates Run instances for a runchain from its wiring,
    if any. Previous Run data is completely removed before proceeding.
    '''

    def precommit_event(self):
        pendingeids = self.cnx.transaction_data.get('pendingeids', ())
        for runchain in self.get_data():
            if runchain.eid in pendingeids or not runchain.wiring:
                continue
            self.cnx.execute('DELETE Run R WHERE S has_runs R, S eid %(s)s',
                                 {'s': runchain.eid})
            with self.cnx.security_enabled():
                runchain.create_runs_from_wiring()


class RunChainAddWiringHook(Hook):
    'Call Run regeneration operation when a Wiring is linked to a RunChain'
    __regid__ = 'processing.runchain_add_wiring'
    __select__ = Hook.__select__ & match_rtype('wiring',)
    events = ('after_add_relation',)

    def __call__(self):
        runchain = self._cw.entity_from_eid(self.eidfrom)
        RunChainWiringGenOperation.get_instance(self._cw).add_data(runchain)


class RunChainWiringUpdateHook(Hook):
    __regid__ = 'processing.runchain_wiring_update'
    __select__ = (Hook.__select__ & is_instance('Wiring')
                  & has_related_entities('wiring', role='object'))
    events = ('after_update_entity',)

    def __call__(self):
        if 'json' in self.entity.cw_edited:
            runchain = self.entity.reverse_wiring[0]
            RunChainWiringGenOperation.get_instance(self._cw).add_data(runchain)


class OutputValueCopyOp(Operation):

    def precommit_event(self):
        rtype = 'value_file' if self.oval.vtype == 'File' else 'value'
        rql = ('SET IV %(rtype)s V WHERE IV from_run R, IV from_output OD, '
               'OV param_def OD, OV %(rtype)s V, OV value_of_run R, '
               'OV eid %%(o)s')
        self.cnx.execute(rql % dict(rtype=rtype), {'o': self.oval.eid})


class OutputValuesCreationHook(Hook):
    __regid__ = 'processing.output_values_creation'
    __select__ = Hook.__select__ & match_rtype('value_of_run')
    events = ('after_add_relation',)

    def __call__(self):
        # When a run chain is defined, we need to copy output values of a run
        # into input values of the next. The WHERE condition in
        # OutputValueCopyOp's rql query ensures the current ParameterValue is
        # related to a run chain
        entity = self._cw.entity_from_eid(self.eidfrom)
        if entity.ptype == 'output':
            OutputValueCopyOp(self._cw, oval=entity)


# Run workflow management ######################################################

class RunCompleteParamsOp(DataOperationMixIn, LateOperation):

    def postcommit_event(self):
        for run in self.get_data():
            wf_run = run.cw_adapt_to('IWorkflowable')
            # if run is in setup state and ready, pass the complete_params
            # transition in an internal session as this is an automatic
            # transition not allowed from non manager users
            if wf_run.state == 'wfs_run_setup' and run.is_ready():
                with self.cnx.repo.internal_cnx() as cnx:
                    new_wf_run = cnx.entity_from_eid(run.eid).cw_adapt_to(
                        'IWorkflowable')
                    new_wf_run.fire_transition('wft_run_complete_params')
                    cnx.commit()


class RunSetInitialStateHook(Hook):
    __regid__ = 'processing.run_set_initial_state'
    __select__ = Hook.__select__ & is_instance('Run')
    events = ('after_add_entity',)
    category = 'workflow'

    def __call__(self):
        RunCompleteParamsOp.get_instance(self._cw).add_data(self.entity)


class SetLastInputValueFiresRunCompleteParams(Hook):
    __regid__ = 'processing.last_ival_set_fires_run_complete_params'
    __select__ = (Hook.__select__
                  & has_related_entities('value_of_run', 'subject')
                  & ~ is_instance('ParameterValueFile')
                  )
    events = ('after_update_entity',)
    category = 'workflow'

    def __call__(self):
        RunCompleteParamsOp.get_instance(self._cw).add_data(self.entity.run)


class LastParamValueFileSetFiresRunCompleteParamsHook(Hook):
    __regid__ = 'processing.last_pvalfile_set_fires_run_complete_params'
    __select__ = Hook.__select__ & match_rtype('value_file')
    events = ('after_add_relation',)
    category = 'workflow'

    def __call__(self):
        entity = self._cw.entity_from_eid(self.eidfrom)
        # selector does not guarantee it is input parameter value: it could be
        # an output too
        if entity.ptype == 'input':
            RunCompleteParamsOp.get_instance(self._cw).add_data(entity.run)


# RunChain workflow management ####################################################

class RunChainRunTransitionHook(Hook):
    __regid__ = 'processing.runchain_run_transition'
    __select__ = Hook.__select__ & on_fire_transition('RunChain', 'wft_runchain_run')
    events = ('after_add_entity',)
    category = 'workflow'

    def __call__(self):
        for run in self.entity.for_entity.has_runs:
            wf_run = run.cw_adapt_to('IWorkflowable')
            wf_run.fire_transition_if_possible('wft_run_queue')


class ResetRunChainInitialStateOp(DataOperationMixIn, Operation):

    def precommit_event(self):
        for runchain in self.get_data():
            if self.cnx.deleted_in_transaction(runchain.eid):
                continue
            wf_runchain = runchain.cw_adapt_to('IWorkflowable')
            assert wf_runchain.state in ('wfs_runchain_setup', 'wfs_runchain_ready'), wf_runchain.state
            wf_runchain.fire_transition_if_possible('wft_runchain_generate')


class HasRunsFiresRunChainGenerateHook(Hook):
    __regid__ = 'processing.has_runs_fires_runchain_generate'
    __select__ = Hook.__select__ & match_rtype('has_runs')
    events = ('after_add_relation',)
    category = 'workflow'

    def __call__(self):
        runchain = self._cw.entity_from_eid(self.eidfrom)
        ResetRunChainInitialStateOp.get_instance(self._cw).add_data(runchain)


class RunChainCheckCompleteOp(DataOperationMixIn, Operation):

    def precommit_event(self):
        for runchain in self.get_data():
            # if runchain has all its run in the completed state, it's completed
            if all(run.cw_adapt_to('IWorkflowable').state == 'wfs_run_completed'
                   for run in runchain.has_runs):
                wf_runchain = runchain.cw_adapt_to('IWorkflowable')
                wf_runchain.fire_transition_if_possible('wft_runchain_complete')


class RunCompleteTransitionHook(Hook):
    __regid__ = 'processing.run_complete_transition'
    __select__ = Hook.__select__ & on_fire_transition('Run', 'wft_run_complete')
    events = ('after_add_entity',)
    category = 'workflow'

    def __call__(self):
        run = self.entity.for_entity
        if run.reverse_has_runs:
            runchain = run.reverse_has_runs[0]
            RunChainCheckCompleteOp.get_instance(self._cw).add_data(runchain)


class RunErrorTransitionHook(Hook):
    __regid__ = 'processing.run_error_transition'
    __select__ = Hook.__select__ & on_fire_transition('Run', 'wft_run_error')
    events = ('after_add_entity',)
    category = 'workflow'

    def __call__(self):
        run = self.entity.for_entity
        if run.reverse_has_runs:
            wf_runchain = run.reverse_has_runs[0].cw_adapt_to('IWorkflowable')
            wf_runchain.fire_transition_if_possible('wft_runchain_error')
