"""Tests for all TI-based estimators in ``alchemlyb``.

"""
import pytest

import pandas as pd

from alchemlyb.parsing import gmx
from alchemlyb.parsing import amber
from alchemlyb.parsing import gomc
from alchemlyb.estimators import TI
import alchemtest.gmx
import alchemtest.amber
import alchemtest.gomc


def gmx_benzene_coul_dHdl():
    dataset = alchemtest.gmx.load_benzene()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['Coulomb']])

    return dHdl

def gmx_benzene_vdw_dHdl():
    dataset = alchemtest.gmx.load_benzene()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['VDW']])

    return dHdl

def gmx_expanded_ensemble_case_1_dHdl():
    dataset = alchemtest.gmx.load_expanded_ensemble_case_1()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['AllStates']])

    return dHdl

def gmx_expanded_ensemble_case_2_dHdl():
    dataset = alchemtest.gmx.load_expanded_ensemble_case_2()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['AllStates']])

    return dHdl

def gmx_expanded_ensemble_case_3_dHdl():
    dataset = alchemtest.gmx.load_expanded_ensemble_case_3()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['AllStates']])

    return dHdl

def gmx_water_particle_with_total_energy_dHdl():
    dataset = alchemtest.gmx.load_water_particle_with_total_energy()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['AllStates']])

    return dHdl

def gmx_water_particle_with_potential_energy_dHdl():
    dataset = alchemtest.gmx.load_water_particle_with_potential_energy()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['AllStates']])

    return dHdl

def gmx_water_particle_without_energy_dHdl():
    dataset = alchemtest.gmx.load_water_particle_without_energy()

    dHdl = pd.concat([gmx.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['AllStates']])

    return dHdl

def amber_simplesolvated_charge_dHdl():
    dataset = alchemtest.amber.load_simplesolvated()

    dHdl = pd.concat([amber.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['charge']])

    return dHdl

def amber_simplesolvated_vdw_dHdl():
    dataset = alchemtest.amber.load_simplesolvated()

    dHdl = pd.concat([amber.extract_dHdl(filename, T=300)
                      for filename in dataset['data']['vdw']])

    return dHdl

def gomc_benzene_dHdl():
    dataset = alchemtest.gomc.load_benzene()

    dHdl = pd.concat([gomc.extract_dHdl(filename, T=298)
                      for filename in dataset['data']])

    return dHdl


class TIestimatorMixin:
    T = 300
    kT_amber = amber.k_b * T

    @pytest.mark.parametrize('X_delta_f', ((gmx_benzene_coul_dHdl(), 3.089, 0.02157),
                                           (gmx_benzene_vdw_dHdl(), -3.056, 0.04863),
                                           (gmx_expanded_ensemble_case_1_dHdl(), 76.220, 0.15568),
                                           (gmx_expanded_ensemble_case_2_dHdl(), 76.247, 0.15889),
                                           (gmx_expanded_ensemble_case_3_dHdl(), 76.387, 0.12532),
                                           (gmx_water_particle_with_total_energy_dHdl(), -11.696, 0.091775),
                                           (gmx_water_particle_with_potential_energy_dHdl(), -11.751, 0.091149),
                                           (gmx_water_particle_without_energy_dHdl(), -11.687, 0.091604),
                                           (amber_simplesolvated_charge_dHdl(), -60.114/kT_amber, 0.08186/kT_amber),
                                           (amber_simplesolvated_vdw_dHdl(), 3.824/kT_amber, 0.13254/kT_amber),
                                           (gomc_benzene_dHdl(), -0.89811, 0.071435)))
    def test_get_delta_f(self, X_delta_f):
        est = self.cls().fit(X_delta_f[0])
        delta_f = est.delta_f_.iloc[0, -1]
        d_delta_f = est.d_delta_f_.iloc[0, -1]

        assert X_delta_f[1] == pytest.approx(delta_f, rel=1e-3)
        assert X_delta_f[2] == pytest.approx(d_delta_f, rel=1e-3)

class TestTI(TIestimatorMixin):
    """Tests for TI.

    """
    cls = TI
