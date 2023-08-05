# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-dataprocessing entity's classes"""

from subprocess import Popen, PIPE, list2cmdline
import sys

from cubicweb import Binary
from cubicweb.predicates import is_instance
from cubicweb.view import EntityAdapter


def process_type_from_etype(etype):
    """Return the type of data process from etype name"""
    return etype[len('Data'):-len('Process')].lower()


def fspath_from_eid(cnx, eid):
    """Return fspath for an entity with `data` attribute stored in BFSS"""
    # XXX this assumes the file is managed by BFSS.
    rset = cnx.execute('Any fspath(D) WHERE X data D, X eid %(feid)s',
                       {'feid': eid})
    if not rset:
        raise Exception('Could not find file system path for #%d.' % eid)
    return rset[0][0].read()


class DataProcessAdapter(EntityAdapter):
    """Interface for data processes"""
    __regid__ = 'IDataProcess'
    __select__ = (EntityAdapter.__select__ &
                  is_instance('DataTransformationProcess',
                              'DataValidationProcess'))

    @property
    def process_type(self):
        """The type of data process"""
        return process_type_from_etype(self.entity.cw_etype)

    def state_name(self, name):
        """Return the full workflow state name given a short name"""
        wfs = 'wfs_dataprocess_' + name
        wf = self.entity.cw_adapt_to('IWorkflowable').current_workflow
        if wf.state_by_name(wfs) is None:
            raise ValueError('invalid state name "%s"' % name)
        return wfs

    def tr_name(self, name):
        """Return the full workflow transition name given a short name"""
        wft = 'wft_dataprocess_' + name
        wf = self.entity.cw_adapt_to('IWorkflowable').current_workflow
        if wf.transition_by_name(wft) is None:
            raise ValueError('invalid transition name "%s"' % name)
        return wft

    def fire_workflow_transition(self, trname, **kwargs):
        """Fire transition identified by *short* name `trname` of the
        underlying workflowable entity.
        """
        tr = self.tr_name(trname)
        iwf = self.entity.cw_adapt_to('IWorkflowable')
        return iwf.fire_transition(tr, **kwargs)

    @property
    def process_script(self):
        """The process script attached to entity"""
        if self.entity.process_script:
            assert len(self.entity.process_script) == 1  # schema
            return self.entity.process_script[0]

    def add_input(self, inputfile):
        """Add an input file to the underlying data process"""
        self.entity.cw_set(process_input_file=inputfile)

    def build_output(self, inputfile, data, **kwargs):
        """Return an ouput File produced from `inputfile` with `data` as
        content.
        """
        return self._cw.create_entity('File', data=Binary(data),
                                      data_name=inputfile.data_name,
                                      data_format=inputfile.data_format,
                                      produced_by=self.entity, **kwargs)

    def execute_script(self, inputfile):
        """Execute script in a subprocess using ``inputfile``.

        Eventually set process output file and return subprocess return
        code and subprocess stderr.
        """
        datapath = fspath_from_eid(self._cw, inputfile.eid)
        script = self.process_script
        scriptpath = fspath_from_eid(self._cw, script.implemented_by[0].eid)
        cmdline = [sys.executable, scriptpath, datapath]
        proc = Popen(cmdline, stdout=PIPE, stderr=PIPE)
        self.info('starting subprocess with pid %s: %s',
                  proc.pid, list2cmdline(cmdline))
        stdoutdata, stderrdata = proc.communicate()
        if proc.returncode:
            self.info('subprocess terminated abnormally (exit code %d)',
                      proc.returncode)
        if self.process_type == 'transformation':
            if stdoutdata:
                feid = self.build_output(inputfile, stdoutdata).eid
                self.info(
                    'created File #%d from input file #%d and script #%d',
                    feid, inputfile.eid, self.process_script.eid)
            else:
                # XXX raise?
                self.info('no standard output produced by Script #%d',
                          script.eid)
        return proc.returncode, unicode(stderrdata, errors='ignore')

    def finalize(self, returncode,  stderr):
        """Finalize a data process firing the proper transition."""
        if returncode:
            self.fire_workflow_transition('error', comment=stderr)
        else:
            self.fire_workflow_transition('complete', comment=stderr)
