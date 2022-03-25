"""
This is a boilerplate pipeline 'model_stoch'
generated using Kedro 0.17.6
"""


from typing import Dict, Callable, Any
import pandas as pd
import pulp
import logging
log = logging.getLogger(__name__)


def construct_model_stoch(timing: Dict, config: Dict, production_pv: pd.DataFrame, demand_ev: pd.DataFrame) -> pulp.LpProblem:

    print("model config: ", config)
    print(production_pv)
    print(demand_ev)

    # my_vehicles = ['car1']  # config['vehicles']
    my_vehicles = config['vehicles']
    my_vehicle_scenarios = demand_ev.index.get_level_values(
        "scenario").unique()

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
    assert E_EL_MAX >= 0
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
    E_EV_MAX = config["E_EV_CAP"]
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

    print('max EVpower: ', demand_ev.power.max())
    for v in my_vehicles:
        for s in my_vehicle_scenarios:
            assert demand_ev.SOC_kWh.loc[v, 0, s] <= E_EV_MAX[v]
            assert demand_ev.SOC_kWh.loc[v, 0, s] >= 0
            for t in Periods:
                #assert demand_ev.power.loc[v, t, s] <= P_EV_MAX[v]
                # fix outliers in EV power consumption
                if demand_ev.power.loc[v, t, s] >= P_EV_MAX[v]*2:
                    demand_ev.power.loc[v, t, s] = P_EV_MAX[v]*2

    # Model creation
    model = pulp.LpProblem("StochastikmodellLadestation", pulp.LpMinimize)

    ###################################################################
    # Entscheidungsvariablen
    ###################################################################

    # NetworkGrid
    n_out = pulp.LpVariable.dicts(
        "GridDraw", [(t, s) for t in Periods for s in my_vehicle_scenarios], lowBound=0, upBound=P_NE_MAX, cat="Continuous"
    )
    n_out_act = pulp.LpVariable.dicts("GridDrawActive", [(
        t, s) for t in Periods for s in my_vehicle_scenarios], cat="Binary")
    n_out_ceil = pulp.LpVariable(
        "GridDrawCeiling", lowBound=0, upBound=P_NE_MAX, cat="Continuous"
    )
    n_out_exp = pulp.LpVariable.dicts(
        "GridDrawExpectedValue", Periods, lowBound=0, upBound=P_NE_MAX, cat="Continuous"
    )

    n_in = pulp.LpVariable.dicts(
        "GridFeed", [(t, s) for t in Periods for s in my_vehicle_scenarios], lowBound=0, upBound=P_NE_MAX, cat="Continuous"
    )
    n_in_act = pulp.LpVariable.dicts(
        "GridFeedActive", [(t, s) for t in Periods for s in my_vehicle_scenarios], cat="Binary")

    # Battery
    b_in = pulp.LpVariable.dicts(
        "BatteryCharge", [(t, s) for t in Periods for s in my_vehicle_scenarios], lowBound=0, upBound=P_EL_MAX, cat="Continuous"
    )
    b_out = pulp.LpVariable.dicts(
        "BatteryDischarge", [(t, s) for t in Periods for s in my_vehicle_scenarios], lowBound=0, upBound=P_EL_MAX, cat="Continuous"
    )
    b_in_act = pulp.LpVariable.dicts(
        "BatteryChargeActive", [(t, s) for t in Periods for s in my_vehicle_scenarios], cat="Binary")
    b_out_act = pulp.LpVariable.dicts(
        "BatteryDischargeActive", [(t, s) for t in Periods for s in my_vehicle_scenarios], cat="Binary")

    B = pulp.LpVariable.dicts(
        "BatterySOC", [(t, s) for t in Instants for s in my_vehicle_scenarios], lowBound=0, upBound=E_EL_MAX, cat="Continuous"
    )

    # Electric Vehicles
    ev_in = pulp.LpVariable.dicts(
        "EVCharge",
        [(v, t, s)
         for v in my_vehicles for t in Periods for s in my_vehicle_scenarios],
        # lowBound=0,
        # upBound=P_EV_MAX,
        cat="Continuous",
    )
    for v in my_vehicles:
        for t in Periods:
            for s in my_vehicle_scenarios:
                ev_in[(v, t, s)].lowBound = 0
                ev_in[(v, t, s)].upBound = P_EV_MAX[v]

    ev_in_act = pulp.LpVariable.dicts(
        "EVChargeActive", [(v, t, s) for v in my_vehicles for t in Periods for s in my_vehicle_scenarios], cat="Binary"
    )
    ev_in_tot = pulp.LpVariable.dicts(
        "EVChargeTotal", [(t, s) for t in Periods for s in my_vehicle_scenarios], lowBound=0, cat="Continuous"
    )

    EV = pulp.LpVariable.dicts(
        "EVSOC",
        [(v, t, s)
         for v in my_vehicles for t in Instants for s in my_vehicle_scenarios],
        # lowBound=E_EV_MIN,
        # upBound=E_EV_MAX,
        cat="Continuous",
    )
    for v in my_vehicles:
        for t in Instants:
            for s in my_vehicle_scenarios:
                EV[(v, t, s)].lowBound = 0
                EV[(v, t, s)].upBound = E_EV_MAX[v]

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

    model += (1/P_NE_MAX)*n_out_ceil - \
        .5*(1/len(my_vehicles))*(1/len(my_vehicle_scenarios))*pulp.lpSum([(1/E_EV_MAX[v])*EV[(v, t, s)] for v, t, s in demand_ev[demand_ev.loadend == True].index.values]) - \
        .5*(1/len(my_vehicles))*(1/len(my_vehicle_scenarios)) * \
        pulp.lpSum([(1/E_EV_MAX[v])*EV[(v, T, s)]
                   for v in my_vehicles for s in my_vehicle_scenarios])

    #model += n_out_ceil + (1/T)*(1/len(my_vehicle_scenarios))*pulp.lpSum(n_out)

    ###############
    # Constraints
    ###############

    for t in Periods:  # loop through all periods

        # Expected Value of Grid Draw
        model += n_out_exp[t] == pulp.lpSum([n_out[(t, s)]*(1/len(my_vehicle_scenarios))
                                             for s in my_vehicle_scenarios])
        # max. grid draw => Target formulation of MiniMax problem
        # model += n_out_exp[t] <= n_out_ceil

        for s in my_vehicle_scenarios:  # loop through all EV scenarios

            # strict condition that all n_out values should be minimized
            model += n_out[(t, s)] <= n_out_ceil

            # special constraints to collapse scenarios in stage 1 for ease of implementation
            if t == 0 and s > 0:
                model += n_out[(t, 0)] == n_out[(t, s)]
                model += n_out_act[(t, 0)] == n_out_act[(t, s)]
                model += n_in[(t, 0)] == n_in[(t, s)]
                model += n_in_act[(t, 0)] == n_in_act[(t, s)]

                model += b_out[(t, 0)] == b_out[(t, s)]
                model += b_out_act[(t, 0)] == b_out_act[(t, s)]
                model += b_in[(t, 0)] == b_in[(t, s)]
                model += b_in_act[(t, 0)] == b_in_act[(t, s)]
                model += B[(t, 0)] == B[(t, s)]

                model += ev_in_tot[(t, 0)] == ev_in_tot[(t, s)]

            # balance equation
            model += (
                n_out[(t, s)] + b_out[(t, s)] + production_pv.PV_kW[t]
                == n_in[(t, s)] + b_in[(t, s)] + ev_in_tot[(t, s)]
            )

            # min./max. grid draw & anti-concurrency
            model += n_out[(t, s)] <= n_out_act[(t, s)] * P_NE_MAX
            model += n_in[(t, s)] <= n_in_act[(t, s)] * P_NE_MAX
            model += n_in_act[(t, s)] + n_out_act[(t, s)] <= 1

            # min./max. (dis)charging power of battery & anti-concurrency
            model += b_in[(t, s)] <= b_in_act[(t, s)] * P_EL_MAX
            model += b_in[(t, s)] >= b_in_act[(t, s)] * P_EL_MIN
            model += b_out[(t, s)] <= b_out_act[(t, s)] * P_EL_MAX
            model += b_out[(t, s)] >= b_out_act[(t, s)] * P_EL_MIN
            model += b_in_act[(t, s)] + b_out_act[(t, s)] <= 1

            # special constraints for LiLa behaviour
            # don't charge battery while drawing power from grid
            model += n_out_act[(t, s)] + b_in_act[(t, s)] <= 1
            # don't discharge battery to grid
            model += n_in_act[(t, s)] + b_out_act[(t, s)] <= 1

            # sum up all load coming from electric vehicles
            model += ev_in_tot[(t, s)] == pulp.lpSum([ev_in[(v, t, s)]
                                                      for v in my_vehicles])

            # keep track of battery SOC including losses
            model += (
                B[(t+1, s)]
                == B[(t, s)] * S_EL + (P_EL_ETA * b_in[(t, s)] - (1 / P_EL_ETA) * b_out[(t, s)]) * M_DT
            )

            for v in my_vehicles:

                # special constraints to collapse scenarios in stage 1 for ease of implementation
                if t == 0 and s > 0:
                    model += ev_in[(v, t, 0)] == ev_in[(v, t, s)]
                    model += ev_in_act[(v, t, 0)] == ev_in_act[(v, t, s)]
                    model += EV[(v, t, 0)] == EV[(v, t, s)]

                # keep track of EV SOC
                model += (
                    EV[(v, t+1, s)]
                    == EV[(v, t, s)] * S_EV
                    + (
                        P_EV_ETA * ev_in[(v, t, s)]
                        - demand_ev.power.loc[v, t, s] *
                        demand_ev.driving.loc[v, t, s] / P_EV_ETA
                    )
                    * M_DT
                )
                # min./max. ev charging power
                model += (
                    ev_in[(v, t, s)]
                    >= ev_in_act[(v, t, s)] * demand_ev.loadable.loc[v, t, s] * P_EV_MIN[v]
                )
                model += (
                    ev_in[(v, t, s)]
                    <= ev_in_act[(v, t, s)] * demand_ev.loadable.loc[v, t, s] * P_EV_MAX[v]
                )
                model += ev_in_act[(v, t, s)] >= 0
                model += ev_in_act[(v, t, s)] <= 1

                # trickle charge to 50% as soon as plugged in as default
                model += ev_in_act[(v, t, s)] >= .5 - \
                    EV[(v, t, s)]*(1/E_EV_MAX[v])

    for s in my_vehicle_scenarios:
        # initial conditions
        # model += B[0, s] == B[T, s]  # E_EL_CAP*.1 #E_EL_BEG
        model += B[0, s] == production_pv.BESS_kWh[0]

        for v in my_vehicles:
            if demand_ev.SOC_kWh.loc[v, 0, s] > 0:  # only use initial values if non-zero
                model += EV[(v, 0, s)] == demand_ev.SOC_kWh.loc[v, 0, s]
            else:  # total discharge unlikely, assuming 50% charge instead to retain feasibility
                model += EV[(v, 0, s)] == E_EV_MAX[v]*.5

    # calculate PV KPIs
    model += wPro == pulp.lpSum(production_pv.PV_kW)
    model += wVer == pulp.lpSum([ev_in_tot[(t, s)]*(1/len(my_vehicle_scenarios))
                                 for t in Periods for s in my_vehicle_scenarios])
    model += wBez == pulp.lpSum([n_out[(t, s)]*(1/len(my_vehicle_scenarios))
                                 for t in Periods for s in my_vehicle_scenarios])
    model += wEin == pulp.lpSum([n_in[(t, s)]*(1/len(my_vehicle_scenarios))
                                 for t in Periods for s in my_vehicle_scenarios])

    # set constants for postprocessing
    model += cPeriods == T
    #model += cDeltaT == M_DT

    # Prepare model
    return model
