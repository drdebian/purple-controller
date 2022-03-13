"""
This is a boilerplate pipeline 'model_rule'
generated using Kedro 0.17.6
"""

from typing import Dict, Callable, Any
import pandas as pd
import pulp
import logging
log = logging.getLogger(__name__)


def construct_model_rule(timing: Dict, config: Dict, production_pv: pd.DataFrame, demand_ev: pd.DataFrame) -> pulp.LpProblem:

    print("model config: ", config)
    print(production_pv)
    print(demand_ev)

    # my_vehicles = ['car1']  # config['vehicles']
    my_vehicles = config['vehicles']

    # timing and scope
    M_DT = timing["M_DT"]  # model length of period in hours
    assert 0 < M_DT <= 1
    M_LA = timing["M_LA"]  # model lookahead number of periods
    assert M_LA > 1

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
    assert P_NE_MAX > 0

    # electric storage
    E_EL_MAX = config["E_EL_CAP"]  # max. energy level to charge to
    assert E_EL_MAX > 0
    # E_EL_MIN = config["E_EL_MIN"]  # min. energy level to drain to
    # max. battery (dis)charging power in kW
    P_EL_MAX = config["P_EL_MAX"]
    assert P_EL_MAX > 0
    # min. battery charging power in kW
    P_EL_MIN = config["P_EL_MIN"]
    assert P_EL_MIN <= P_EL_MAX
    P_EL_ETA = config["P_EL_ETA"]  # (dis)charging efficiency
    assert 0 < P_EL_ETA <= 1
    # self-discharge percentage of battery per day
    S_EL = config["S_EL"]  # discharge factor per period
    assert 0 <= S_EL <= 1

    # electric vehicles
    # my_vehicles = demand_ev.index.get_level_values("vehicle").unique()
    # EV capacity in kWh (Nissan Leaf 2016: (40) or 62 kWh)
    E_EV_MAX = config["E_EV_CAP"]
    #E_EV_MIN = constants["E_EV_MIN"]
    # max. EV charging power in kW (A*phases*V)
    P_EV_MAX = config["P_EV_MAX"]
    # min. EV charging power in kW (A*phases*V)
    P_EV_MIN = config["P_EV_MIN"]
    P_EV_ETA = config["P_EV_ETA"]  # EV charging efficiency
    assert 0 < P_EV_ETA <= 1
    # self-discharge percentage of electric vehicles per day
    S_EV = config["S_EV"]  # discharge factor per period
    assert 0 <= S_EV <= 1

    # demand and production
    assert demand_ev.power.min() >= 0
    assert demand_ev.SOC_kWh.min() >= 0
    assert production_pv.PV_kW.min() >= 0
    assert production_pv.BESS_kWh.min() >= 0

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
        "BatterySOC", Instants, lowBound=0, upBound=E_EL_MAX, cat="Continuous"
    )

    # Electric Vehicles
    ev_in = pulp.LpVariable.dicts(
        "EVCharge",
        [(v, t) for v in my_vehicles for t in Periods],
        # lowBound=0,
        # upBound=P_EV_MAX,
        cat="Continuous",
    )
    for v in my_vehicles:
        for t in Periods:
            ev_in[(v, t)].lowBound = 0
            ev_in[(v, t)].upBound = P_EV_MAX[v]

    ev_in_act = pulp.LpVariable.dicts(
        "EVChargeActive", [(v, t) for v in my_vehicles for t in Periods], cat="Binary"
    )
    ev_in_tot = pulp.LpVariable.dicts(
        "EVChargeTotal", Periods, lowBound=0, cat="Continuous"
    )
    # binary variables to couple ev_in to EV based on rules
    I1 = pulp.LpVariable.dicts(
        "Interval1", [(v, t) for v in my_vehicles for t in Periods], cat="Binary"
    )
    I2 = pulp.LpVariable.dicts(
        "Interval2", [(v, t) for v in my_vehicles for t in Periods], cat="Binary"
    )
    I3 = pulp.LpVariable.dicts(
        "Interval3", [(v, t) for v in my_vehicles for t in Periods], cat="Binary"
    )
    I4 = pulp.LpVariable.dicts(
        "Interval4", [(v, t) for v in my_vehicles for t in Periods], cat="Binary"
    )
    I5 = pulp.LpVariable.dicts(
        "Interval5", [(v, t) for v in my_vehicles for t in Periods], cat="Binary"
    )

    EV = pulp.LpVariable.dicts(
        "EVSOC",
        [(v, t) for v in my_vehicles for t in Instants],
        # lowBound=0,
        # upBound=E_EV_MAX,
        cat="Continuous",
    )
    for v in my_vehicles:
        for t in Instants:
            EV[(v, t)].lowBound = 0
            EV[(v, t)].upBound = E_EV_MAX[v]

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

    model += pulp.lpSum([n_out[t]*t for t in Periods]) + \
        (1/T)*pulp.lpSum(n_out) - pulp.lpSum(EV)
    #model += pulp.lpSum(n_out)
    # model += pulp.lpSum([n_out[t]*t for t in Periods])
    #model += pulp.lpSum([-EV[(v, T)]*(1/E_EV_MAX[v]) for v in my_vehicles])

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
        ##model += b_out_act[t] >= 1 - production_pv.PV_kW[t]

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
                >= ev_in_act[(v, t)] * demand_ev.loadable.loc[v, t] * P_EV_MIN[v]
            )
            model += (
                ev_in[(v, t)]
                <= ev_in_act[(v, t)] * demand_ev.loadable.loc[v, t] * P_EV_MAX[v]
            )
            model += ev_in_act[(v, t)] >= 0
            model += ev_in_act[(v, t)] <= 1

            # trickle charge to 80% as soon as plugged in as default
            # model += ev_in_act[(v, t)] >= .8 - EV[(v, t)]*(1/E_EV_MAX[v])

            # limit charging power based on SOC
            # model += ev_in[(v, t)] <= P_EV_MAX[v] - \
            #     (P_EV_MAX[v]-P_EV_MIN[v])/E_EV_MAX[v]*EV[(v, t)]

            # SOS1 constraint on I1-I5 intervals
            model += I1[(v, t)] + I2[(v, t)] + I3[(v, t)] + I4[(v, t)] + I5[(v, t)] == 1

            # upper bounds
            model += EV[(v, t)] <= E_EV_MAX[v] * \
                (1 - 4/5*I1[(v, t)] - 3/5*I2[(v, t)] - 2/5*I3[(v, t)] - 1/5*I4[(v, t)])

            # lower bounds
            model += EV[(v, t)] >= E_EV_MAX[v] * \
                (0 + 1/5*I2[(v, t)] + 2/5*I3[(v, t)] + 3/5*I4[(v, t)] + 4/5*I5[(v, t)])

            # limit charging power based on EVSOC-interval
            model += ev_in[(v, t)] <= P_EV_MAX[v] - (P_EV_MAX[v]-P_EV_MIN[v]) * \
                (1/4*I2[(v, t)]+2/4*I3[(v, t)]+3/4*I4[(v, t)]+4/4*I5[(v, t)])

    # initial conditions
    # model += B[0] == B[T]
    model += B[0] == production_pv.BESS_kWh[0]  # soc_inits['BESS']  # E_EL_BEG

    for v in my_vehicles:
        # soc_inits[v]  # demand_ev.EVSOC.loc[v, 0]
        if demand_ev.SOC_kWh.loc[v, 0] > 0:  # only use initial values if non-zero
            model += EV[(v, 0)] == demand_ev.SOC_kWh.loc[v, 0]
        else:  # total discharge unlikely, assuming 50% charge instead to retain feasibility
            model += EV[(v, 0)] == E_EV_MAX[v]*.5

        # model += EV[(v, 0)] == 10  # demand_ev.SOC_kWh.loc[v, 0]
        # model += EV[(v, 0)] <= EV[(v, T)]
        # model += EV[(v, 0)] >= EV[(v, T)] - P_EV_MIN * M_DT

        # model += EV[(v, 0)] == EV[(v, T)] + \
        #     EV_under[(v, T)] - EV_over[(v, T)]
        # pass

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
