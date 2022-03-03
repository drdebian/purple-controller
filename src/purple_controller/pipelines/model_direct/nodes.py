"""
This is a boilerplate pipeline 'model_direct'
generated using Kedro 0.17.6
"""

"""
This is a boilerplate pipeline 'model_pred'
generated using Kedro 0.17.6
"""

from typing import Dict, Callable, Any
import pandas as pd
import pulp
import logging
log = logging.getLogger(__name__)
# plt.style.use('ggplot')


def construct_model_direct(timing: Dict, config: Dict, production_pv: pd.DataFrame, demand_ev: pd.DataFrame) -> pulp.LpProblem:

    # timing and scope
    M_DT = timing["M_DT"]  # model length of period in hours
    M_LA = timing["M_LA"]  # model lookahead number of periods

    # Time
    T = int(round(M_LA/M_DT, 0))
    assert T >= 1
    # Achtung: Reformulierung von Periods wegen 0-indizierter Listen.
    Periods = range(0, T)
    Instants = range(0, T + 1)

    # infrastructure
    # power grid
    # maximum power draw/delivery allowed from/to grid in kW
    P_NE_MAX = config["P_NE_MAX"]

    # electric storage
    E_EL_MAX = config["E_EL_MAX"]  # max. energy level to charge to
    E_EL_MIN = config["E_EL_MIN"]  # min. energy level to drain to
    # max. battery (dis)charging power in kW
    P_EL_MAX = config["P_EL_MAX"]
    # min. battery charging power in kW
    P_EL_MIN = config["P_EL_MIN"]
    P_EL_ETA = config["P_EL_ETA"]  # (dis)charging efficiency
    # self-discharge percentage of battery per day
    S_EL = config["S_EL"]  # discharge factor per period

    # electric vehicles
    # my_vehicles = demand_ev.index.get_level_values("vehicle").unique()
    my_vehicles = config['vehicles']
    # EV capacity in kWh (Nissan Leaf 2016: (40) or 62 kWh)
    E_EV_MAX = config["E_EV_CAP"]
    #E_EV_MIN = constants["E_EV_MIN"]
    # max. EV charging power in kW (A*phases*V)
    P_EV_MAX = config["P_EV_MAX"]
    # min. EV charging power in kW (A*phases*V)
    P_EV_MIN = config["P_EV_MIN"]
    P_EV_ETA = config["P_EV_ETA"]  # EV charging efficiency
    # self-discharge percentage of electric vehicles per day
    S_EV = config["S_EV"]  # discharge factor per period

    # Model creation
    model = pulp.LpProblem("BasismodellLadestation", pulp.LpMinimize)

    ###################################################################
    # Entscheidungsvariablen
    ###################################################################

    # NetworkGrid
    n_out = pulp.LpVariable.dicts(
        "GridDraw", Periods, lowBound=0, upBound=P_NE_MAX, cat="Continuous"
    )
    n_out_act = pulp.LpVariable.dicts("GridDrawActive", Periods, cat="Binary")
    n_out_ceil = pulp.LpVariable(
        "GridDrawCeiling", lowBound=0, upBound=P_NE_MAX, cat="Continuous"
    )

    n_in = pulp.LpVariable.dicts(
        "GridFeed", Periods, lowBound=0, upBound=P_NE_MAX, cat="Continuous"
    )
    n_in_act = pulp.LpVariable.dicts("GridFeedActive", Periods, cat="Binary")

    # Battery
    b_in = pulp.LpVariable.dicts(
        "BatteryCharge", Periods, lowBound=0, upBound=P_EL_MAX, cat="Continuous"
    )
    b_out = pulp.LpVariable.dicts(
        "BatteryDischarge", Periods, lowBound=0, upBound=P_EL_MAX, cat="Continuous"
    )
    b_in_act = pulp.LpVariable.dicts(
        "BatteryChargeActive", Periods, cat="Binary")
    b_out_act = pulp.LpVariable.dicts(
        "BatteryDischargeActive", Periods, cat="Binary")

    B = pulp.LpVariable.dicts(
        "BatterySOC", Instants, lowBound=E_EL_MIN, upBound=E_EL_MAX, cat="Continuous"
    )

# TODO: indexed bounds!!
    # Electric Vehicles
    ev_in = pulp.LpVariable.dicts(
        "EVCharge",
        [(v, t) for v in my_vehicles for t in Periods],
        lowBound=0,
        upBound=P_EV_MAX,
        cat="Continuous",
    )
    ev_in_act = pulp.LpVariable.dicts(
        "EVChargeActive", [(v, t) for v in my_vehicles for t in Periods], cat="Binary"
    )
    ev_in_tot = pulp.LpVariable.dicts(
        "EVChargeTotal", Periods, lowBound=0, cat="Continuous"
    )

    EV = pulp.LpVariable.dicts(
        "EVSOC",
        [(v, t) for v in my_vehicles for t in Instants],
        lowBound=0,
        upBound=E_EV_MAX,
        cat="Continuous",
    )

    # helper variables for PV KPI calculation
    wPro = pulp.LpVariable("PVProducedTotal", lowBound=0, cat="Continuous")
    wEin = pulp.LpVariable("GridFeedTotal", lowBound=0, cat="Continuous")
    wVer = pulp.LpVariable("PowerDemandTotal", lowBound=0, cat="Continuous")
    wBez = pulp.LpVariable("GridDrawTotal", lowBound=0, cat="Continuous")

    # helper variables for postprocessing
    cPeriods = pulp.LpVariable("Periods", lowBound=0, cat="Integer")
    #cDeltaT = pulp.LpVariable("DeltaT", lowBound=0, cat="Continuous")

    ###############
    # Zielfunktion
    ###############

    model += pulp.lpSum([n_out[t]*t for t in Periods]) + (1/T)*pulp.lpSum(n_out)

    ###############
    # Constraints
    ###############

    for t in Periods:

        model += (
            n_out[t] + b_out[t] + production_pv.PV_kW[t]
            == n_in[t] + b_in[t] + ev_in_tot[t]
        )  # balance equation

        model += n_out[t] <= n_out_ceil  # max. grid draw => Target formulation

        # min./max. grid draw & anti-concurrency
        model += n_out[t] <= n_out_act[t] * P_NE_MAX
        model += n_in[t] <= n_in_act[t] * P_NE_MAX
        model += n_in_act[t] + n_out_act[t] <= 1

        # min./max. (dis)charging power of battery & anti-concurrency
        model += b_in[t] <= b_in_act[t] * P_EL_MAX
        model += b_in[t] >= b_in_act[t] * P_EL_MIN
        model += b_out[t] <= b_out_act[t] * P_EL_MAX
        model += b_out[t] >= b_out_act[t] * P_EL_MIN
        model += b_in_act[t] + b_out_act[t] <= 1

        # special constraints for LiLa behaviour
        # don't charge battery while drawing power from grid
        model += n_out_act[t] + b_in_act[t] <= 1
        # don't discharge battery to grid
        model += n_in_act[t] + b_out_act[t] <= 1
        # allow battery charging if pv production is greater than zero
        #model += b_in_act[t] <= production_pv.PV_kW[t]
        model += b_out_act[t] >= 1 - production_pv.PV_kW[t]
        #model += n_out_act[t] + b_out_act[t] <= 1

        # sum up all load coming from electric vehicles
        model += ev_in_tot[t] == pulp.lpSum([ev_in[(v, t)]
                                             for v in my_vehicles])

        # keep track of battery SOC including losses
        model += (
            B[t + 1]
            == B[t] * S_EL + (P_EL_ETA * b_in[t] - (1 / P_EL_ETA) * b_out[t]) * M_DT
        )

        for v in my_vehicles:
            model += (
                EV[(v, t + 1)]
                == EV[(v, t)] * S_EV
                + (
                    P_EV_ETA * ev_in[(v, t)]
                    - demand_ev.power.loc[v, t] *
                    demand_ev.driving.loc[v, t] / P_EV_ETA
                )
                * M_DT
            )  # keep track of EV SOC
            # min./max. ev charging power
            model += (
                ev_in[(v, t)]
                >= ev_in_act[(v, t)] * demand_ev.loadable.loc[v, t] * P_EV_MIN
            )
            model += (
                ev_in[(v, t)]
                <= ev_in_act[(v, t)] * demand_ev.loadable.loc[v, t] * P_EV_MAX
            )
            model += ev_in_act[(v, t)] >= 0
            model += ev_in_act[(v, t)] <= 1

            # trickle charge to 80% as soon as plugged in as default
            model += ev_in_act[(v, t)] >= .8 - EV[(v, t)]*(1/E_EV_MAX)

    # initial conditions
    # model += B[0] == B[T]  # E_EL_CAP*.1 #E_EL_BEG
    model += B[0] == soc_inits['BESS']  # E_EL_BEG

    for v in my_vehicles:
        model += EV[(v, 0)] == soc_inits[v]  # demand_ev.EVSOC.loc[v, 0]
        # model += EV[(v, 0)] <= EV[(v, T)]
        # model += EV[(v, 0)] >= EV[(v, T)] - P_EV_MIN * M_DT

        # model += EV[(v, 0)] == EV[(v, T)] + \
        #     EV_under[(v, T)] - EV_over[(v, T)]

    # calculate PV KPIs
    model += wPro == pulp.lpSum(production_pv.PV_kW)
    model += wVer == pulp.lpSum(ev_in_tot)
    model += wBez == pulp.lpSum(n_out)
    model += wEin == pulp.lpSum(n_in)

    # set constants for postprocessing
    model += cPeriods == T
    #model += cDeltaT == M_DT

    # Prepare model
    return model
