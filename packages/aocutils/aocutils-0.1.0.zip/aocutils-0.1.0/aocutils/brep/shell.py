# coding: utf-8

r"""shell module of occutils

Classes
-------
Shell
    check()
    analyse()
    faces()
    wires()
    edges()
"""

import logging

import OCC.BRepBuilderAPI
import OCC.TopoDS
import OCC.ShapeAnalysis
import OCC.BRepCheck

import aocutils.topology
import aocutils.brep.base
import aocutils.analyze.global_
import aocutils.exceptions

logger = logging.getLogger(__name__)


class Shell(aocutils.brep.base.BaseObject):
    r"""Shell class

    Parameters
    ----------
    topods_shell : OCC.TopoDS.TopoDS_Shell

    """
    _n = 0

    def __init__(self, topods_shell):
        if not isinstance(topods_shell, OCC.TopoDS.TopoDS_Shell):
            msg = 'need a TopoDS_Shell, got a %s' % topods_shell.__class__
            logger.critical(msg)
            raise aocutils.exceptions.WrongTopologicalType(msg)

        assert not topods_shell.IsNull()

        aocutils.brep.base.BaseObject.__init__(self, topods_shell, 'shell')

        Shell._n += 1

    @property
    def topods_shell(self):
        return self._wrapped_instance

    def check(self):
        r"""Super class abstract method implementation"""
        # super(Shell, self).check()
        # todo : call BRepCheck_Shell methods
        return OCC.BRepCheck.BRepCheck_Shell(self._wrapped_instance)

    def analyse(self):
        r"""Bad edges of the shell"""
        bad_edges = list()
        ss = OCC.ShapeAnalysis.ShapeAnalysis_Shell()
        ss.LoadShells(self._wrapped_instance)
        if ss.HasFreeEdges():
            bad_edges = [e for e in aocutils.topology.Topo(ss.BadEdges()).edges()]
        return bad_edges

    def faces(self):
        r"""Faces of the shell"""
        return aocutils.topology.Topo(self._wrapped_instance, return_iter=True).faces()

    def wires(self):
        r"""Wires of the shell"""
        return aocutils.topology.Topo(self._wrapped_instance, return_iter=True).wires()

    def edges(self):
        r"""Edges of the shell"""
        return aocutils.topology.Topo(self._wrapped_instance, return_iter=True).edges()
