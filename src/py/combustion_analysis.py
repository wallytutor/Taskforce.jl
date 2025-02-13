# -*- coding: utf-8 -*-
from numbers import Number
import cantera as ct
import logging

Composition = str | dict[str, Number]
""" Composition format for Cantera solutions. """


def solution(mech: str, /, **kwargs):
    """ Create a standard solution from mechanism. """
    try:
        sol = ct.Solution(mech)
    except ct.CanteraError as err:
        logging.error(f"Creating solution with {mech}:\n{err}")
        return

    T = kwargs.get("T", sol.T)
    P = kwargs.get("P", sol.P)
    X = kwargs.get("X", sol.X)

    sol.TPX = T, P, X

    return sol


def chon_complete_combustion(gas: ct.Solution) -> dict[str, float]:
    """ Evaluate complete combustion products for a gas. """
    return {
        "CO2": 1.0 * gas.elemental_mole_fraction("C"),
        "H2O": 0.5 * gas.elemental_mole_fraction("H"),
        "N2":  0.5 * gas.elemental_mole_fraction("N")
    }


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


def mixture_heating_value(
        mech: str,
        X_fuel: Composition,
        T: Number = 273.15,
    ) -> float:
    """ Mixture mass weighted average heating value [MJ/kg]. """
    gas = solution(mech, T=T, P=ct.one_atm, X=X_fuel)
    Y_fuel = gas.mass_fraction_dict()

    # Mass weighted average:
    Hv = sum(Y * species_lower_heating_value(gas, name, T)
             for name, Y in Y_fuel.items())

    return float(Hv)


def power_supply(
        mech: str,
        mdot: Number,
        X_fuel: Composition,
        /,
        **kwargs
    ) -> float:
    """ Total fuel computed power supply [W].
    
    Parameters
    ----------
    mech: str
        Kinetics mechanism used for evaluation.
    mdot: Number
        Fuel mass flow rate [kg/h].
    X_fuel: Composition
        Fuel composition [mole fractions].
    """
    Hv = mixture_heating_value(mech, X_fuel, **kwargs)
    return (mdot / 3600.0) * (Hv * 1.0e+06)
