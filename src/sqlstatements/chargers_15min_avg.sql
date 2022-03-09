with ctea1 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'station1' as station,
        a.*
    from charger1 a
),
ctea2 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'station2' as station,
        a.*
    from charger2 a
),
ctea3 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'station3' as station,
        a.*
    from charger3 a
),
ctea4 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'station4' as station,
        a.*
    from charger4 a
),
ctea5 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'station5' as station,
        a.*
    from charger5 a
),
cte0 as (
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg(coalesce([activePower-W], 0)), 0) as [activePower-W],
        round(avg(coalesce([phase1-volt], 0)), 0) as [phase1-volt],
        round(avg(coalesce([phase1-curr], 0)), 0) as [phase1-curr],
        round(avg(coalesce([phase1-power], 0)), 0) as [phase1-power],
        round(avg(coalesce([phase2-volt], 0)), 0) as [phase2-volt],
        round(avg(coalesce([phase2-curr], 0)), 0) as [phase2-curr],
        round(avg(coalesce([phase2-power], 0)), 0) as [phase2-power],
        round(avg(coalesce([phase3-volt], 0)), 0) as [phase3-volt],
        round(avg(coalesce([phase3-curr], 0)), 0) as [phase3-curr],
        round(avg(coalesce([phase3-power], 0)), 0) as [phase3-power],
        round(avg(coalesce([calculatedPower], 0)), 0) as [calculatedPower],
        max(coalesce([state], 0)) as [state],
        count(*) as cntMeasurements
    from ctea1 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg(coalesce([activePower-W], 0)), 0) as [activePower-W],
        round(avg(coalesce([phase1-volt], 0)), 0) as [phase1-volt],
        round(avg(coalesce([phase1-curr], 0)), 0) as [phase1-curr],
        round(avg(coalesce([phase1-power], 0)), 0) as [phase1-power],
        round(avg(coalesce([phase2-volt], 0)), 0) as [phase2-volt],
        round(avg(coalesce([phase2-curr], 0)), 0) as [phase2-curr],
        round(avg(coalesce([phase2-power], 0)), 0) as [phase2-power],
        round(avg(coalesce([phase3-volt], 0)), 0) as [phase3-volt],
        round(avg(coalesce([phase3-curr], 0)), 0) as [phase3-curr],
        round(avg(coalesce([phase3-power], 0)), 0) as [phase3-power],
        round(avg(coalesce([calculatedPower], 0)), 0) as [calculatedPower],
        max(coalesce([state], 0)) as [state],
        count(*) as cntMeasurements
    from ctea2 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg(coalesce([activePower-W], 0)), 0) as [activePower-W],
        round(avg(coalesce([phase1-volt], 0)), 0) as [phase1-volt],
        round(avg(coalesce([phase1-curr], 0)), 0) as [phase1-curr],
        round(avg(coalesce([phase1-power], 0)), 0) as [phase1-power],
        round(avg(coalesce([phase2-volt], 0)), 0) as [phase2-volt],
        round(avg(coalesce([phase2-curr], 0)), 0) as [phase2-curr],
        round(avg(coalesce([phase2-power], 0)), 0) as [phase2-power],
        round(avg(coalesce([phase3-volt], 0)), 0) as [phase3-volt],
        round(avg(coalesce([phase3-curr], 0)), 0) as [phase3-curr],
        round(avg(coalesce([phase3-power], 0)), 0) as [phase3-power],
        round(avg(coalesce([calculatedPower], 0)), 0) as [calculatedPower],
        max(coalesce([state], 0)) as [state],
        count(*) as cntMeasurements
    from ctea3 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg(coalesce([activePower-W], 0)), 0) as [activePower-W],
        round(avg(coalesce([phase1-volt], 0)), 0) as [phase1-volt],
        round(avg(coalesce([phase1-curr], 0)), 0) as [phase1-curr],
        round(avg(coalesce([phase1-power], 0)), 0) as [phase1-power],
        round(avg(coalesce([phase2-volt], 0)), 0) as [phase2-volt],
        round(avg(coalesce([phase2-curr], 0)), 0) as [phase2-curr],
        round(avg(coalesce([phase2-power], 0)), 0) as [phase2-power],
        round(avg(coalesce([phase3-volt], 0)), 0) as [phase3-volt],
        round(avg(coalesce([phase3-curr], 0)), 0) as [phase3-curr],
        round(avg(coalesce([phase3-power], 0)), 0) as [phase3-power],
        round(avg(coalesce([calculatedPower], 0)), 0) as [calculatedPower],
        max(coalesce([state], 0)) as [state],
        count(*) as cntMeasurements
    from ctea4 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg(coalesce([activePower-W], 0)), 0) as [activePower-W],
        round(avg(coalesce([phase1-volt], 0)), 0) as [phase1-volt],
        round(avg(coalesce([phase1-curr], 0)), 0) as [phase1-curr],
        round(avg(coalesce([phase1-power], 0)), 0) as [phase1-power],
        round(avg(coalesce([phase2-volt], 0)), 0) as [phase2-volt],
        round(avg(coalesce([phase2-curr], 0)), 0) as [phase2-curr],
        round(avg(coalesce([phase2-power], 0)), 0) as [phase2-power],
        round(avg(coalesce([phase3-volt], 0)), 0) as [phase3-volt],
        round(avg(coalesce([phase3-curr], 0)), 0) as [phase3-curr],
        round(avg(coalesce([phase3-power], 0)), 0) as [phase3-power],
        round(avg(coalesce([calculatedPower], 0)), 0) as [calculatedPower],
        max(coalesce([state], 0)) as [state],
        count(*) as cntMeasurements
    from ctea5 a
    group by a.TimeDate15m

)
select b.*
from cte0 b 
    /* where [phase1-volt] > 0
        */
    /* where b.timestamp >= datetime('now', '-8 days')
        */