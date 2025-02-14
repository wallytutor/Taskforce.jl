# -*- coding: utf-8 -*-
from numbers import Number
import cantera as ct
import logging

Composition = str | dict[str, Number]
""" Composition format for Cantera solutions. """

T_NORMAL = 273.15
""" Normal state reference temperature [K]. """

P_NORMAL = 101325.0
""" Normal state reference temperature [K]. """


class Solution:
    """ Wrapper around Cantera's solution object. """
    def __init__(self, mech: str, /, **kwargs) -> None:
        self._mech = mech
        self._sol = self._handle_init(mech, **kwargs)

    @staticmethod
    def _handle_init(mech, **kwargs):
        """ Create a standard solution from mechanism. """
        sol = ct.Solution(mech)
        T = kwargs.get("T", sol.T)
        P = kwargs.get("P", sol.P)
        X = kwargs.get("X", sol.mole_fraction_dict())
        sol.TPX = T, P, X
        return sol

    def density(self, /, **kwargs) -> float:
        """ Density of provided mixture under normal conditions [kg/m³]. """
        T = kwargs.get("T", self._sol.T)
        P = kwargs.get("P", self._sol.P)
        X = kwargs.get("X", None)
        X = X if X else self._sol.mole_fraction_dict()
        sol = self._handle_init(self._mech, X=X, T=T, P=P)
        return sol.density_mass

    def density_normal(self, /, X: Composition = None) -> float:
        """ Density of provided mixture under normal conditions [kg/m³]. """
        return self.density(X=X, T=T_NORMAL, P=P_NORMAL)

    @property
    def solution(self) -> ct.Solution:
        """ Provides access to the wrapped solution object. """
        return self._sol


class FuelMixture:
    """ Create a fuel mixture for combustion calculations.

    Parameters
    ----------
    mech: str
        Kinetics mechanism used for evaluation of fuel properties.
    X: Composition
        Fuel composition [mole fractions].
    """
    def __init__(self, mech: str, X: Composition, /, **kwargs) -> None:
        self._sol = self._handle_init(mech, X, **kwargs)
        self._lhv = self._lower_heating_value()

    @staticmethod
    def _handle_init(mech, X, **kwargs):
        """ Create a standard mixture from mechanism. """
        T = kwargs.get("T", T_NORMAL)
        P = kwargs.get("P", P_NORMAL)
        sol = Solution(mech, X=X, T=T, P=P)
        return sol

    @staticmethod
    def species_lower_heating_value(
            gas: ct.Solution,
            fuel: Composition,
            T: Number,
        ) -> float:
        """ Returns the lower heating value of species [MJ/kg]. """
        gas.TP = T, ct.one_atm
        gas.set_equivalence_ratio(1.0, fuel, "O2: 1.0")
        h1 = gas.enthalpy_mass
        Y_fuel = gas[fuel].Y[0]

        gas.TPX = None, None, chon_complete_combustion(gas)
        h2 = gas.enthalpy_mass

        return -1.0e-06 * (h2 - h1) / Y_fuel

    def _lower_heating_value(self):
        """ Mixture mass weighted average heating value [MJ/kg]. """
        sol = self._sol.solution
        Hv = sum(Y * self.species_lower_heating_value(sol, name, sol.T)
                 for name, Y in sol.mass_fraction_dict().items())
        return float(Hv)

    def power_supply(self, mdot: Number) -> float:
        """ Total fuel computed power supply [kW].

        Parameters
        ----------
        mdot: Number
            Fuel mass flow rate [kg/h].
        """
        return 0.001 * (mdot / 3600.0) * (self._lhv * 1.0e+06)

    @property
    def lower_heating_value(self):
        """ Mixture mass weighted average heating value [MJ/kg]. """
        return self._lhv


def chon_complete_combustion(gas: ct.Solution) -> dict[str, float]:
    """ Evaluate complete combustion products for a gas. """
    return {
        "CO2": 1.0 * gas.elemental_mole_fraction("C"),
        "H2O": 0.5 * gas.elemental_mole_fraction("H"),
        "N2":  0.5 * gas.elemental_mole_fraction("N")
    }


# def adiabatic_combustion_flue(X_fuel, X_oxid, T_fuel, T_oxid)