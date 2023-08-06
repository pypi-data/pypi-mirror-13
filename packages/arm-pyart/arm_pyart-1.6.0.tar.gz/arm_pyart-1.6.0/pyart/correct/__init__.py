"""
========================================
Radar Corrections (:mod:`pyart.correct`)
========================================

.. currentmodule:: pyart.correct

Correct radar fields.

Velocity unfolding
==================

.. autosummary::
    :toctree: generated/

    dealias_fourdd
    dealias_unwrap_phase
    dealias_region_based

Other corrections
=================

.. autosummary::
    :toctree: generated/

    calculate_attenuation
    phase_proc_lp

Helper functions
================

.. autosummary::
    :toctree: generated/

    find_time_in_interp_sonde

"""

from .dealias import dealias_fourdd, find_time_in_interp_sonde
from .attenuation import calculate_attenuation
from .phase_proc import phase_proc_lp
# for backwards compatibility GateFilter available in the correct namespace
from ..filters.gatefilter import GateFilter, moment_based_gate_filter
from .unwrap import dealias_unwrap_phase
from .region_dealias import dealias_region_based

__all__ = [s for s in dir() if not s.startswith('_')]
