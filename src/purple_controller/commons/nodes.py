"""
general functions used in multiple pipelines
"""

from typing import Dict, Callable, Any, Tuple
import pandas as pd
import numpy as np
import pulp
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import logging
import time
import datetime as dt

from sqlalchemy import DDL

log = logging.getLogger(__name__)
computation_log = logging.getLogger("purple.computation")


def load_lila_config(config_lila: Dict, config_cars: Dict, constants: Dict) -> Dict:
    """Function to parse original system configuration files into format suitable for use in a model

    Args:
        config_lila (Dict): Nested dictionary containing LiLa configuration parameters
        config_cars (Dict): Nested dictionary containing car configuration parameters
        constants: Dictionary subsection from parameters.yaml

    Returns:
        Dict: Flattened dictionary containing consolidated configuration for use in model
    """

    # model_config = {}
    model_config = constants.copy()  # use defaults from parameters.yaml

    model_config['E_EL_CAP'] = config_lila['LiLa']['battery']['capacity']
    #model_config['P_EL_MAX'] = config_lila['LiLa']['battery']['maxChargingPower']
    #model_config['P_EL_MIN'] = config_lila['LiLa']['battery']['maxDischargePower']
    model_config['P_PV_CAP'] = config_lila['LiLa']['pv']['maxPower']
    # model_config['P_PV_ETA'] = constants['P_PV_ETA']
    # model_config['P_EL_MAX'] = constants['P_EL_MAX']
    # model_config['P_EL_MIN'] = constants['P_EL_MIN']

    model_config['P_CS_MAX'] = {}
    for cs in config_lila['LiLa']['chargingstations']:
        station = 'charger' + str(cs['stationId'])
        model_config['P_CS_MAX'][station] = cs['maxChargingPower']

    model_config['E_EV_CAP'] = {}
    model_config['P_EV_MAX'] = {}
    model_config['P_EV_MIN'] = {}
    model_config['vehicles'] = []
    for car in config_cars['cars']:
        vehicle = 'car'+str(car['carID'])
        if car['capacity']:
            model_config['E_EV_CAP'][vehicle] = car['capacity']
            model_config['P_EV_MAX'][vehicle] = car['maxChargingPower']
            model_config['P_EV_MIN'][vehicle] = car['minChargingPower']
            model_config['vehicles'].append(vehicle)

    print(model_config)

    # print(config_cars)
    # print(config_lila)

    return model_config


def get_model_timestamps(timing: Dict) -> Dict[str, pd.Timestamp]:

    if timing['M_ST'] == 'now':
        start = pd.Timestamp.now()
    else:
        start = pd.Timestamp(timing['M_ST'])

    # + pd.Timedelta(1*int(60*timing['M_DT']), 'T')
    start = start.round(str(int(60*timing['M_DT']))+'T')

    my_now = start  # + pd.Timedelta(i*int(60*c1['M_DT']), 'T')

    # calculate current iteration timebracket for history data
    #my_past_from = my_now - pd.Timedelta(timing['M_LB']*24*int(60*timing['M_DT']), 'T')
    my_past_from = my_now - pd.Timedelta(timing['M_LB'], 'D')
    my_past_to = my_now - pd.Timedelta(1*int(60*timing['M_DT']), 'T')

    my_timestamps = {}

    my_timestamps['now'] = my_now
    my_timestamps['past_from'] = my_past_from
    my_timestamps['past_to'] = my_past_to

    print(my_timestamps)

    return my_timestamps


def show_model_timestamps(timestamps: Dict):
    print(timestamps)


def get_current_pv_data(my_pv: pd.DataFrame, my_timestamps: Dict) -> pd.DataFrame:
    my_timestamp = my_timestamps['now']
    try:  # try getting the right row according to the timestamp
        pv_temp = my_pv.loc[my_timestamp:my_timestamp].copy()
    except:  # if that fails, get the latest known row instead
        pv_temp = my_pv.iloc[-1].copy()

    pv_temp.reset_index(inplace=True, drop=True)
    print(pv_temp)
    return pv_temp


def get_current_ev_data(my_ev: pd.DataFrame, my_timestamps: Dict) -> pd.DataFrame:
    #my_timestamp = my_timestamps['now']
    # ^^^^ this has to be ignored due to the possibility of data gaps
    # ^^^^ as a consequence, the last record is being used for "now"

    ev_temp = my_ev.copy()
    ev_temp = ev_temp.reset_index(drop=False)
    ev_temp = ev_temp.groupby('vehicle').max()
    ev_temp.reset_index(inplace=True, drop=False)

    ev_max_index = list(zip(ev_temp.vehicle, ev_temp.timestamp))
    my_index = pd.MultiIndex.from_tuples(ev_max_index)

    # ev_temp = my_ev.xs(my_timestamp, level='timestamp').copy()
    # # alternative: ev_data.loc[pd.IndexSlice[:, start:start],:]

    ev_temp = my_ev.copy()
    ev_temp = ev_temp.loc[my_index, :]
    ev_temp.reset_index(inplace=True, drop=False)
    ev_temp['period'] = 0
    ev_temp.drop(['timestamp'], axis=1, inplace=True)
    ev_temp.set_index(['vehicle', 'period'], inplace=True)

    print(ev_temp)
    return ev_temp  # .astype(float)


def get_history_pv_data(my_pv: pd.DataFrame, my_timestamps: Dict) -> pd.DataFrame:
    pv_temp = my_pv.loc[my_timestamps['past_from']:my_timestamps['past_to']].copy()
    print(pv_temp)
    return pv_temp


def get_history_ev_data(my_ev: pd.DataFrame, my_timestamps: Dict) -> pd.DataFrame:
    ev_temp = my_ev.loc[pd.IndexSlice[:, my_timestamps['past_from']                                      :my_timestamps['past_to']], :].copy()

    print(ev_temp)
    return ev_temp


def predict_pv_data(my_pv: pd.DataFrame, timing: Dict) -> pd.DataFrame:
    pv_temp = my_pv.copy()
    pv_temp['timestamp'] = pv_temp.index
    pv_temp.reset_index(drop=True, inplace=True)
    pv_temp['period'] = pv_temp.index % int((timing['M_LA']/timing['M_DT']))
    pv_temp = pv_temp.groupby('period').mean()
    print(pv_temp)
    return pv_temp


def predict_ev_data(my_ev: pd.DataFrame, timing: Dict) -> pd.DataFrame:
    ev_temp = my_ev.copy()
    ev_temp.reset_index(drop=False, inplace=True)
    ev_temp['period'] = ev_temp.groupby(
        'vehicle').cumcount() % int((timing['M_LA']/timing['M_DT']))
    ev_temp = ev_temp.groupby(['vehicle', 'period']).mean()
    ev_temp['driving'] = np.sign(ev_temp['driving'])
    #ev_temp['loadable'] = np.sign(ev_temp['loadable'])
    ev_temp['loadable'] = ev_temp['loadable'] >= 0.5
    ev_temp.loc[ev_temp['driving'] > 0, 'loadable'] = False
    print(ev_temp)
    return ev_temp


def scenarios_ev_data(my_ev: pd.DataFrame, timing: Dict) -> pd.DataFrame:
    # TODO: handle cases where not all cars have the same number of scenarios!
    ev_temp = my_ev.sort_index().copy()
    ev_temp.reset_index(drop=False, inplace=True)
    ev_temp['period'] = ev_temp.groupby(
        'vehicle').cumcount() % int((timing['M_LA']/timing['M_DT']))
    ev_temp['scenario'] = ev_temp.groupby(['vehicle', 'period']).cumcount()
    ev_temp = ev_temp.groupby(['vehicle', 'period', 'scenario']).mean()
    return ev_temp.sort_index()


def get_model_pv_data(my_current_pv: pd.DataFrame, my_predicted_pv: pd.DataFrame) -> pd.DataFrame:
    pv_temp = pd.concat(
        [my_current_pv, my_predicted_pv.loc[pd.IndexSlice[1:], :]]).sort_index().copy()
    print(pv_temp)
    return pv_temp


def get_model_ev_data(my_current_ev: pd.DataFrame, my_predicted_ev: pd.DataFrame) -> pd.DataFrame:
    ev_temp = pd.concat(
        [my_current_ev, my_predicted_ev.loc[pd.IndexSlice[:, 1:], :]]).sort_index().copy()

    # detect end of loadable period and generate loadend flag
    ev_temp['loadend'] = False
    ev_temp.loc[(ev_temp.loadable > ev_temp.loadable.shift(-1)) &
                (ev_temp.index.get_level_values('period') < max(ev_temp.index.get_level_values('period'))-1), 'loadend'] = True

    # detect end of driving period and generate driveend flag
    ev_temp['driveend'] = False
    ev_temp.loc[(ev_temp.driving > ev_temp.driving.shift(-1)) &
                (ev_temp.index.get_level_values('period') < max(ev_temp.index.get_level_values('period'))-1), 'driveend'] = True

    # detect beginning of loadable period and generate loadbeg flag
    ev_temp['loadbeg'] = False
    ev_temp.loc[(ev_temp.loadable > ev_temp.loadable.shift(-1)) &
                (ev_temp.index.get_level_values('period') < max(ev_temp.index.get_level_values('period'))-1), 'loadbeg'] = True

    my_columns = ['SOC_kWh', 'power', 'driving',
                  'loadable', 'loadend', 'driveend', 'loadbeg']
    ev_temp = ev_temp[my_columns]

    print(ev_temp)
    return ev_temp


def get_model_ev_scenarios(current_ev: pd.DataFrame, scenarios_ev: pd.DataFrame) -> pd.DataFrame:
    my_scenarios = scenarios_ev.index.get_level_values('scenario').unique()
    my_current_ev = current_ev.sort_index().copy()

    appended_data = list()
    for i in my_scenarios:
        my_temp = my_current_ev.copy()
        my_temp['scenario'] = i
        appended_data.append(my_temp)

    ev_temp = pd.concat(appended_data)
    ev_temp.reset_index(drop=False, inplace=True)
    ev_temp.set_index(['vehicle', 'period', 'scenario'], inplace=True)

    ev_temp = pd.concat(
        [ev_temp, scenarios_ev.loc[pd.IndexSlice[:, 1:, :], :]]).copy().sort_index()

    # change index from vehicle-period-scenario to vehicle-scenario-period
    ev_temp.reset_index(drop=False, inplace=True)
    ev_temp.set_index(['vehicle', 'scenario', 'period'], inplace=True)
    ev_temp = ev_temp.sort_index()

    # detect end of loadable period and generate loadend flag
    ev_temp['loadend'] = False
    ev_temp.loc[(ev_temp.loadable > ev_temp.loadable.shift(-1)) &
                (ev_temp.index.get_level_values('period') < max(ev_temp.index.get_level_values('period'))-1), 'loadend'] = True

    # detect end of driving period and generate driveend flag
    ev_temp['driveend'] = False
    ev_temp.loc[(ev_temp.driving > ev_temp.driving.shift(-1)) &
                (ev_temp.index.get_level_values('period') < max(ev_temp.index.get_level_values('period'))-1), 'driveend'] = True

    # detect beginning of loadable period and generate loadbeg flag
    ev_temp['loadbeg'] = False
    ev_temp.loc[(ev_temp.loadable > ev_temp.loadable.shift(-1)) &
                (ev_temp.index.get_level_values('period') < max(ev_temp.index.get_level_values('period'))-1), 'loadbeg'] = True

    # change index back to vehicle-period-scenario
    ev_temp.reset_index(drop=False, inplace=True)
    ev_temp.set_index(['vehicle', 'period', 'scenario'], inplace=True)
    ev_temp = ev_temp.sort_index()

    return ev_temp


# def get_model_soc_inits(constants: Dict, my_current_ev: pd.DataFrame) -> Dict[str, float]:

#     my_soc_inits = {}

#     my_vehicles = list(my_current_ev.index.get_level_values('vehicle').unique())
#     for v in my_vehicles:
#         my_soc_inits[v] = constants['E_EV_BEG']

#     my_soc_inits['BESS'] = constants['E_EL_BEG']

#     print(my_soc_inits)
#     return my_soc_inits


def solve_model(model: pulp.LpProblem, solverparams: Dict) -> pulp.LpProblem:

    tic = time.perf_counter()

    solver = pulp.PULP_CBC_CMD(
        gapRel=solverparams['gap_relative'],
        gapAbs=solverparams['gap_absolute'],
        timeLimit=solverparams['timelimit'],
    )
    result = model.solve(solver)

    toc = time.perf_counter()
    computation_log.info(
        f"Model: Direct Charging. Solution time: {toc - tic:0.3f} seconds.")

    log.info('Model solving state: ' + str(result))

    if result != 1:
        log.error('Model could not be solved!!')
        # print(model)

    return model


def extract_model_solution_dataframes(model: pulp.LpProblem) -> Dict:

    result0 = pd.DataFrame(data=None)
    result1 = pd.DataFrame(data=None)
    result2 = pd.DataFrame(data=None)
    result3 = pd.DataFrame(data=None)
    result = {}

    for v in model.variables():
        namesplit = v.name.split('_')
        basename = namesplit[0]
        #print(basename, len(namesplit))

        if len(namesplit) == 1:  # single value
            result0.loc[0, basename] = v.varValue
        elif len(namesplit) == 2:  # simple index
            if namesplit[1].isnumeric():
                indexval = int(namesplit[1])
                result1.loc[indexval, basename] = v.varValue
        elif len(namesplit) == 3:  # tuple index 2 values
            indexval = ''.join(namesplit[1:])
            if indexval[0] == '(' and indexval[-1] == ')':
                result2.loc[indexval, basename] = v.varValue
        elif len(namesplit) == 4:  # tuple index 3 values
            indexval = ''.join(namesplit[1:])
            if indexval[0] == '(' and indexval[-1] == ')':
                result3.loc[indexval, basename] = v.varValue
        else:
            print('error!!')

    result['result0'] = result0.sort_index().copy()
    result['result1'] = result1.sort_index().copy()

    # convert single tuple-string index into proper multiindex
    if len(result2) > 1:
        result2['tmpindex'] = result2.index
        result2['tmpindex2'] = result2.tmpindex.apply(lambda x: eval(x))
        result2.index = pd.MultiIndex.from_tuples(
            result2.tmpindex2)  # , names=['vehicle', 'period'])
        result2.drop(['tmpindex', 'tmpindex2'], axis=1, inplace=True)
        result['result2'] = result2.sort_index().copy()

    if len(result3) > 1:
        result3['tmpindex'] = result3.index
        result3['tmpindex2'] = result3.tmpindex.apply(lambda x: eval(x))
        result3.index = pd.MultiIndex.from_tuples(
            result3.tmpindex2)  # , names=['vehicle', 'period', 'scenario'])
        result3.drop(['tmpindex', 'tmpindex2'], axis=1, inplace=True)
        result['result3'] = result3.sort_index().copy()

    return result


def store_model_solution_dataframes(solution: Dict) -> Dict:

    # dummy node to store versioned solutions

    return solution


def store_model_solution_tables(result: Dict) -> Tuple:

    my_runningtime = str(dt.datetime.now())

    # store results to database
    result0 = result['result0']
    result1 = result['result1']
    result1.index.names = ['period']
    result1.reset_index(drop=False, inplace=True)
    result2 = result['result2']
    result2.index.names = ['vehicle', 'period']
    result2.reset_index(drop=False, inplace=True)

    # add timestamp for versioning
    result0['runningdate'] = my_runningtime
    result1['runningdate'] = my_runningtime
    result2['runningdate'] = my_runningtime

    return result0, result1, result2


def store_model_solution_tables_stoch(result: Dict) -> Tuple:

    my_runningtime = str(dt.datetime.now())

    # store results to database
    result0 = result['result0']
    result1 = result['result1']
    result1.index.names = ['period']
    result1.reset_index(drop=False, inplace=True)
    result2 = result['result2']
    result2.index.names = ['period', 'scenario']
    result2.reset_index(drop=False, inplace=True)
    result3 = result['result3']
    result3.index.names = ['vehicle', 'period', 'scenario']
    result3.reset_index(drop=False, inplace=True)

    # add timestamp for versioning
    result0['runningdate'] = my_runningtime
    result1['runningdate'] = my_runningtime
    result2['runningdate'] = my_runningtime
    result3['runningdate'] = my_runningtime

    return result0, result1, result2, result3


def plot_sys_timeseries_simple(result: Dict, prodpv: pd.DataFrame, demandev: pd.DataFrame) -> plt.figure:

    result0 = result['result0']
    result1 = result['result1']
    result2 = result['result2']
    result2.index.names = ['vehicle', 'period']

    my_periods = range(0, int(result0.Periods[0]))  # c1['T'])
    my_instants = range(0, int(result0.Periods[0])+1)
    my_vehicles = result2.index.get_level_values('vehicle').unique()
    my_maxgriddraw = max(np.array([result1.GridDraw.loc[t]
                                   for t in my_periods]))

    plt.style.use('ggplot')

    fig, axs = plt.subplots(3, 1, figsize=(13, 13), sharex="col")

    # plot Overview
    axs[0].step(np.array(my_periods), np.array([result1.GridDraw.loc[t]
                                                for t in my_periods]), '.-r', where='post', label='$GridDraw$', lw=3)
    axs[0].axhline(my_maxgriddraw,
                   ls=':', label='$GridDraw Ceiling$')
    axs[0].step(np.array(my_periods), np.array([result1.GridFeed.loc[t]
                                                for t in my_periods]), '.-m', where='post', label='$GridFeed$', lw=3)
    axs[0].step(np.array(my_periods), np.array([result1.BatteryCharge.loc[t]
                                                for t in my_periods]),     '.-g', where='post', label='$BatteryCharge$', lw=3)
    axs[0].step(np.array(my_periods), np.array([result1.BatteryDischarge.loc[t]
                                                for t in my_periods]),     '.-b', where='post', label='$BatteryDischarge$', lw=3)
    axs[0].step(np.array(my_periods), np.array([result1.EVChargeTotal.loc[t] for t in my_periods]),
                '.-k', where='post', label='$EVDraw$', lw=3)
    axs[0].step(np.array(my_periods),
                prodpv.PV_kW,
                ls='-',
                color='yellow',
                where='post',
                label='$PVProduction$',
                lw=3
                )

    at = AnchoredText(
        "$n_{max}$ = " + str(round(my_maxgriddraw, 2)),
        # prop=dict(size=15),
        frameon=True,
        loc='upper center')
    at.patch.set_boxstyle("round, pad=0, rounding_size=.2")
    axs[0].add_artist(at)

    axs[0].set_xlabel('periods')
    axs[0].set_ylabel('Power (kW)')
    axs[0].set_title('Overview')
    axs[0].legend(loc='upper right')  # , fontsize=7)

    # plot individual EV charge/discharge
    for i, v in enumerate(my_vehicles):
        color = 'C' + str(i)
        axs[1].step(my_periods, np.array([result2.EVCharge[v, t] for t in my_periods])
                    - np.array([demandev.power.loc[v, t] for t in my_periods]), '.-', where='post', color=color, label='$'+v+'$')
    axs[1].set_xlabel('periods')
    axs[1].set_ylabel('Power (kW)')
    axs[1].set_title('Power per vehicle')
    axs[1].legend(loc='upper right')

    # plot SOC
    axs[2].plot(my_instants, result1.BatterySOC,
                color='black',
                ls='-',
                label='$Battery$',
                lw=3,
                )
    for i, v in enumerate(my_vehicles):
        color = 'C' + str(i)
        axs[2].plot(my_instants, np.array([result2.EVSOC[v, t] for t in my_instants]),
                    ls='-',
                    color=color,
                    label='$'+v+'$',
                    lw=3
                    )

    axs[2].set_xlabel('instants')
    axs[2].set_ylabel('Energy (kWh)')
    axs[2].set_title('SOC')
    axs[2].legend(loc='upper right')  # , fontsize=7)

    fig.tight_layout()

    return(fig)


def plot_sys_timeseries_stochastic(result: Dict, prodpv: pd.DataFrame, demandev: pd.DataFrame) -> plt.figure:

    result0 = result['result0']
    result2 = result['result2']
    result3 = result['result3']
    result2.index.names = ['period', 'scenario']
    result3.index.names = ['vehicle', 'period', 'scenario']

    my_periods = range(0, int(result0.Periods[0]))  # c1['T'])
    my_instants = range(0, int(result0.Periods[0])+1)
    my_vehicles = result3.index.get_level_values('vehicle').unique()
    my_scenarios = result2.index.get_level_values('scenario').unique()

    plt.style.use('ggplot')

    fig, axs = plt.subplots(3, 1, figsize=(13, 13), sharex="col")

    # plot Overview
    # GridDraw average
    avg = np.array([result2.GridDraw.loc[(t)].mean() for t in my_periods])
    lb = np.maximum(
        avg - np.array([result2.GridDraw.loc[(t)].std() for t in my_periods]), 0)
    ub = avg + np.array([result2.GridDraw.loc[(t)].std()
                         for t in my_periods])
    color = 'red'
    axs[0].step(np.array(my_periods), avg,
                ls='--',
                lw=3,
                # color='red',
                color=color,
                where='post',
                label='$\mathbb{E}\left[ GridDraw \\right]$'
                )
    axs[0].step(np.array(my_periods), lb,
                ls=':',
                lw=1,
                where='post',
                color=color  # ,
                )
    axs[0].step(np.array(my_periods), ub,
                ls=':',
                lw=1,
                where='post',
                color=color
                )
    axs[0].fill_between(my_periods, avg, lb, hatch='//',
                        alpha=.1, color=color, step='post')
    axs[0].fill_between(my_periods, avg, ub, hatch='\\\\',
                        alpha=.1, color=color, step='post')

    # GridFeed average
    avg = np.array([result2.GridFeed.loc[(t)].mean() for t in my_periods])
    lb = np.maximum(
        avg - np.array([result2.GridFeed.loc[(t)].std() for t in my_periods]), 0)
    ub = avg + np.array([result2.GridFeed.loc[(t)].std()
                         for t in my_periods])
    color = 'magenta'
    axs[0].step(np.array(my_periods), avg,
                ls='--',
                lw=3,
                # color='red',
                color=color,
                where='post',
                label='$\mathbb{E}\left[ GridFeed \\right]$'
                )
    axs[0].step(np.array(my_periods), lb,
                ls=':',
                lw=1,
                where='post',
                color=color  # ,
                )
    axs[0].step(np.array(my_periods), ub,
                ls=':',
                lw=1,
                where='post',
                color=color
                )
    axs[0].fill_between(my_periods, avg, lb, hatch='//',
                        alpha=.1, color=color, step='post')
    axs[0].fill_between(my_periods, avg, ub, hatch='\\\\',
                        alpha=.1, color=color, step='post')

    # EVChargeTotal average
    avg = np.array([result2.EVChargeTotal.loc[(t)].mean()
                    for t in my_periods])
    lb = np.maximum(
        avg - np.array([result2.EVChargeTotal.loc[(t)].std() for t in my_periods]), 0)
    ub = avg + np.array([result2.EVChargeTotal.loc[(t)].std()
                         for t in my_periods])
    color = 'black'
    axs[0].step(np.array(my_periods), avg,
                ls='--',
                lw=3,
                color=color,
                where='post',
                label='$\mathbb{E}\left[ EVChargeTotal \\right]$'
                )
    axs[0].step(np.array(my_periods), lb,
                ls=':',
                lw=1,
                where='post',
                color=color  # ,
                )
    axs[0].step(np.array(my_periods), ub,
                ls=':',
                lw=1,
                where='post',
                color=color
                )
    axs[0].fill_between(my_periods, avg, lb, hatch='//',
                        alpha=.1, color=color, step='post')
    axs[0].fill_between(my_periods, avg, ub, hatch='\\\\',
                        alpha=.1, color=color, step='post')

    # BatteryCharge average
    avg = np.array([result2.BatteryCharge.loc[(t)].mean()
                    for t in my_periods])
    lb = np.maximum(
        avg - np.array([result2.BatteryCharge.loc[(t)].std() for t in my_periods]), 0)
    ub = avg + np.array([result2.BatteryCharge.loc[(t)].std()
                         for t in my_periods])
    color = 'green'
    axs[0].step(np.array(my_periods), avg,
                ls='--',
                lw=3,
                color=color,
                where='post',
                label='$\mathbb{E}\left[ BatteryCharge \\right]$'
                )
    axs[0].step(np.array(my_periods), lb,
                ls=':',
                lw=1,
                where='post',
                color=color  # ,
                )
    axs[0].step(np.array(my_periods), ub,
                ls=':',
                lw=1,
                where='post',
                color=color
                )
    axs[0].fill_between(my_periods, avg, lb, hatch='//',
                        alpha=.1, color=color, step='post')
    axs[0].fill_between(my_periods, avg, ub, hatch='\\\\',
                        alpha=.1, color=color, step='post')

    # BatteryDischarge average
    avg = np.array([result2.BatteryDischarge.loc[(t)].mean()
                    for t in my_periods])
    lb = np.maximum(
        avg - np.array([result2.BatteryDischarge.loc[(t)].std() for t in my_periods]), 0)
    ub = avg + np.array([result2.BatteryDischarge.loc[(t)].std()
                         for t in my_periods])
    color = 'blue'
    axs[0].step(np.array(my_periods), avg,
                ls='--',
                lw=3,
                color=color,
                where='post',
                label='$\mathbb{E}\left[ BatteryDischarge \\right]$'
                )
    axs[0].step(np.array(my_periods), lb,
                ls=':',
                lw=1,
                where='post',
                color=color  # ,
                )
    axs[0].step(np.array(my_periods), ub,
                ls=':',
                lw=1,
                where='post',
                color=color
                )
    axs[0].fill_between(my_periods, avg, lb, hatch='//',
                        alpha=.1, color=color, step='post')
    axs[0].fill_between(my_periods, avg, ub, hatch='\\\\',
                        alpha=.1, color=color, step='post')

    axs[0].axhline(result0.GridDrawCeiling[0],
                   ls=':', label='$GridDraw Ceiling$')
    axs[0].step(my_periods, prodpv.PV_kW,
                ls='-',
                lw=5,
                color='yellow',
                where='post',
                label='$PVProduction$')
    #color = 'C' + str(1)
    for s in my_scenarios:
        axs[0].step(np.array(my_periods), np.array([result2.loc[(t, s), 'GridDraw'] for t in my_periods]),
                    ls='-',
                    lw=2,
                    color='red',
                    where='post',
                    alpha=1/len(my_scenarios),
                    label='GridDraw Scenarios' if s == 0 else ''
                    )
        axs[0].step(np.array(my_periods), np.array([result2.loc[(t, s), 'GridFeed'] for t in my_periods]),
                    ls='-',
                    lw=2,
                    color='magenta',
                    where='post',
                    alpha=1/len(my_scenarios),
                    label='GridFeed Scenarios' if s == 0 else ''
                    )
        axs[0].step(np.array(my_periods), np.array([result2.loc[(t, s), 'EVChargeTotal'] for t in my_periods]),
                    ls='-',
                    lw=2,
                    color='black',
                    where='post',
                    alpha=1/len(my_scenarios),
                    label='EVChargeTotal Scenarios' if s == 0 else ''
                    )

        axs[0].step(np.array(my_periods), np.array([result2.loc[(t, s), 'BatteryCharge'] for t in my_periods]),
                    ls='-',
                    lw=2,
                    color='green',
                    where='post',
                    alpha=1/len(my_scenarios),
                    label='BatteryCharge Scenarios' if s == 0 else ''
                    )
        axs[0].step(np.array(my_periods), np.array([result2.loc[(t, s), 'BatteryDischarge'] for t in my_periods]),
                    ls='-',
                    lw=2,
                    color='blue',
                    where='post',
                    alpha=1/len(my_scenarios),
                    label='BatteryDischarge Scenarios' if s == 0 else ''
                    )

    axs[0].axvline(0.95, color='white', lw=4, ls='-.', label='Stage 1->2')

    at = AnchoredText(
        "$n_{max}$ = " + str(round(result0.GridDrawCeiling[0], 2)),
        # prop=dict(size=15),
        frameon=True,
        loc='upper center')
    at.patch.set_boxstyle("round, pad=0, rounding_size=.2")
    axs[0].add_artist(at)

    axs[0].set_xlabel('periods')
    axs[0].set_ylabel('Power (kW)')
    axs[0].set_title('Overview')
    axs[0].legend(loc='upper right')  # , fontsize=7)

    # plot individual EV charge/discharge
    # EVCharge average
    for i, v in enumerate(my_vehicles):
        #np.array([result3.EVCharge[v, t] for t in my_periods]) - np.array([demandev.power.loc[v, t] for t in my_periods])
        avg = np.array([(result3.EVCharge.loc[v, t] -
                         demandev.power.loc[v, t]).mean() for t in my_periods])
        lb = avg - np.array([(result3.EVCharge.loc[v, t] -
                              demandev.power.loc[v, t]).std() for t in my_periods])
        ub = avg + np.array([(result3.EVCharge.loc[v, t] - demandev.power.loc[v, t]).std()
                             for t in my_periods])
        color = 'C' + str(i)
        axs[1].step(np.array(my_periods), avg,
                    ls='--',
                    lw=3,
                    where='post',
                    color=color,
                    label='$\mathbb{E}\left[ '+v+' \\right]$'
                    )
        axs[1].step(np.array(my_periods), lb,
                    ls=':',
                    lw=1,
                    where='post',
                    color=color  # ,
                    )
        axs[1].step(np.array(my_periods), ub,
                    ls=':',
                    lw=1,
                    where='post',
                    color=color
                    )
        axs[1].fill_between(my_periods, avg, lb,
                            hatch='//', alpha=.1, color=color, step='post')
        axs[1].fill_between(my_periods, avg, ub,
                            hatch='\\\\', alpha=.1, color=color, step='post')

    for s in my_scenarios:
        for i, v in enumerate(my_vehicles):
            color = 'C' + str(i)
            axs[1].step(np.array(my_periods), np.array([result3.EVCharge.loc[v, t, s] for t in my_periods]),
                        ls='-',
                        lw=2,
                        where='post',
                        color=color,
                        alpha=1/len(my_scenarios),
                        label=v+' Scenarios' if s == 0 else ''
                        )

    axs[1].axvline(0.95, color='white', lw=4, ls='-.', label='Stage 1->2')

    axs[1].set_xlabel('periods')
    axs[1].set_ylabel('Power (kW)')
    axs[1].set_title('Power per vehicle')
    axs[1].legend(loc='upper right', fontsize=7)

    # plot SOC
    # BatterySOC average
    avg = np.array([result2.BatterySOC.loc[(t)].mean() for t in my_instants])
    lb = np.maximum(
        avg - np.array([result2.BatterySOC.loc[(t)].std() for t in my_instants]), 0)
    ub = avg + np.array([result2.BatterySOC.loc[(t)].std()
                         for t in my_instants])
    color = 'black'
    axs[2].plot(np.array(my_instants), avg,
                ls='--',
                lw=3,
                color=color,
                label='$\mathbb{E}\left[ Battery \\right]$'
                )
    axs[2].plot(np.array(my_instants), lb,
                ls=':',
                lw=1,
                color=color  # ,
                )
    axs[2].plot(np.array(my_instants), ub,
                ls=':',
                lw=1,
                color=color
                )
    axs[2].fill_between(my_instants, avg, lb, hatch='//',
                        alpha=.1, color=color)
    axs[2].fill_between(my_instants, avg, ub, hatch='\\\\',
                        alpha=.1, color=color)

    # EVSOC average
    for i, v in enumerate(my_vehicles):
        avg = np.array([result3.EVSOC.loc[v, t].mean() for t in my_instants])
        lb = np.maximum(
            avg - np.array([result3.EVSOC.loc[v, t].std() for t in my_instants]), 0)
        ub = avg + np.array([result3.EVSOC.loc[v, t].std()
                             for t in my_instants])
        color = 'C' + str(i)
        axs[2].plot(np.array(my_instants), avg,
                    ls='--',
                    lw=3,
                    color=color,
                    label='$\mathbb{E}\left[ '+v+' \\right]$'
                    )
        axs[2].plot(np.array(my_instants), lb,
                    ls=':',
                    lw=1,
                    color=color  # ,
                    )
        axs[2].plot(np.array(my_instants), ub,
                    ls=':',
                    lw=1,
                    color=color
                    )
        axs[2].fill_between(my_instants, avg, lb,
                            hatch='//', alpha=.1, color=color)
        axs[2].fill_between(my_instants, avg, ub,
                            hatch='\\\\', alpha=.1, color=color)

    for s in my_scenarios:
        axs[2].plot(np.array(my_instants), np.array([result2.loc[(t, s), 'BatterySOC'] for t in my_instants]),
                    ls='-',
                    lw=2,
                    color='black',
                    alpha=1/len(my_scenarios),
                    label='Battery Scenarios' if s == 0 else ''
                    )

        for i, v in enumerate(my_vehicles):
            color = 'C' + str(i)
            axs[2].plot(np.array(my_instants), np.array([result3.EVSOC.loc[v, t, s] for t in my_instants]),
                        ls='-',
                        lw=2,
                        color=color,
                        alpha=1/len(my_scenarios),
                        label=v+' Scenarios' if s == 0 else ''
                        )

    axs[2].axvline(0.95, color='white', lw=4, ls='-.', label='Stage 1->2')

    axs[2].set_xlabel('instants')
    axs[2].set_ylabel('Energy (kWh)')
    axs[2].set_title('SOC')
    axs[2].legend(loc='upper right', fontsize=7)
    fig.tight_layout()

    return(fig)


def get_ev_charge_limits(result: Dict, params: Dict, config: Dict) -> Dict:

    # prepare maximums in case of override
    ev_charge_limits_override = pd.DataFrame()
    ev_charge_limits_override['vehicle'] = config['P_EV_MAX'].keys()
    ev_charge_limits_override['EVCharge'] = config['P_EV_MAX'].values()
    ev_charge_limits_override.set_index('vehicle', inplace=True)
    ev_charge_limits_override = ev_charge_limits_override.EVCharge[:].copy()

    # prepare real data in case of no override
    ev_charge_limits_real = result['result2'].EVCharge[:, 0].copy()

    if params['disable_charging_limits'] == 1:
        print("override detected!")
        ev_charge_limits = ev_charge_limits_override
        print("values for output:")
        print(ev_charge_limits_override)
        print("real values from model:")
        print(ev_charge_limits_real)
    else:
        ev_charge_limits = ev_charge_limits_real
        print(ev_charge_limits)

    return ev_charge_limits


def get_ev_charge_limits_stoch(result: Dict, params: Dict, config: Dict) -> Dict:

    # prepare maximums in case of override
    ev_charge_limits_override = pd.DataFrame()
    ev_charge_limits_override['vehicle'] = config['P_EV_MAX'].keys()
    ev_charge_limits_override['EVCharge'] = config['P_EV_MAX'].values()
    ev_charge_limits_override.set_index('vehicle', inplace=True)
    ev_charge_limits_override = ev_charge_limits_override.EVCharge[:].copy()

    # prepare real data in case of no override
    ev_charge_limits_real = result['result3'].EVCharge[:, 0, 0].copy()

    if params['disable_charging_limits'] == 1:
        print("override detected!")
        ev_charge_limits = ev_charge_limits_override
        print("values for output:")
        print(ev_charge_limits_override)
        print("real values from model:")
        print(ev_charge_limits_real)
    else:
        ev_charge_limits = ev_charge_limits_real
        print(ev_charge_limits)

    return ev_charge_limits
