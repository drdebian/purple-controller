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
ctea6 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'station6' as station,
        a.*
    from charger6 a
),
cte0 as (
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg([activePower-W]), 0) as [activePower-W],
        round(avg([phase1-volt]), 0) as [phase1-volt],
        round(avg([phase1-curr]), 0) as [phase1-curr],
        round(avg([phase1-power]), 0) as [phase1-power],
        round(avg([phase2-volt]), 0) as [phase2-volt],
        round(avg([phase2-curr]), 0) as [phase2-curr],
        round(avg([phase2-power]), 0) as [phase2-power],
        round(avg([phase3-volt]), 0) as [phase3-volt],
        round(avg([phase3-curr]), 0) as [phase3-curr],
        round(avg([phase3-power]), 0) as [phase3-power],
        round(avg([calculatedPower]), 0) as [calculatedPower],
        count(*) as cntMeasurements
    from ctea1 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg([activePower-W]), 0) as [activePower-W],
        round(avg([phase1-volt]), 0) as [phase1-volt],
        round(avg([phase1-curr]), 0) as [phase1-curr],
        round(avg([phase1-power]), 0) as [phase1-power],
        round(avg([phase2-volt]), 0) as [phase2-volt],
        round(avg([phase2-curr]), 0) as [phase2-curr],
        round(avg([phase2-power]), 0) as [phase2-power],
        round(avg([phase3-volt]), 0) as [phase3-volt],
        round(avg([phase3-curr]), 0) as [phase3-curr],
        round(avg([phase3-power]), 0) as [phase3-power],
        round(avg([calculatedPower]), 0) as [calculatedPower],
        count(*) as cntMeasurements
    from ctea2 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg([activePower-W]), 0) as [activePower-W],
        round(avg([phase1-volt]), 0) as [phase1-volt],
        round(avg([phase1-curr]), 0) as [phase1-curr],
        round(avg([phase1-power]), 0) as [phase1-power],
        round(avg([phase2-volt]), 0) as [phase2-volt],
        round(avg([phase2-curr]), 0) as [phase2-curr],
        round(avg([phase2-power]), 0) as [phase2-power],
        round(avg([phase3-volt]), 0) as [phase3-volt],
        round(avg([phase3-curr]), 0) as [phase3-curr],
        round(avg([phase3-power]), 0) as [phase3-power],
        round(avg([calculatedPower]), 0) as [calculatedPower],
        count(*) as cntMeasurements
    from ctea3 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg([activePower-W]), 0) as [activePower-W],
        round(avg([phase1-volt]), 0) as [phase1-volt],
        round(avg([phase1-curr]), 0) as [phase1-curr],
        round(avg([phase1-power]), 0) as [phase1-power],
        round(avg([phase2-volt]), 0) as [phase2-volt],
        round(avg([phase2-curr]), 0) as [phase2-curr],
        round(avg([phase2-power]), 0) as [phase2-power],
        round(avg([phase3-volt]), 0) as [phase3-volt],
        round(avg([phase3-curr]), 0) as [phase3-curr],
        round(avg([phase3-power]), 0) as [phase3-power],
        round(avg([calculatedPower]), 0) as [calculatedPower],
        count(*) as cntMeasurements
    from ctea4 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg([activePower-W]), 0) as [activePower-W],
        round(avg([phase1-volt]), 0) as [phase1-volt],
        round(avg([phase1-curr]), 0) as [phase1-curr],
        round(avg([phase1-power]), 0) as [phase1-power],
        round(avg([phase2-volt]), 0) as [phase2-volt],
        round(avg([phase2-curr]), 0) as [phase2-curr],
        round(avg([phase2-power]), 0) as [phase2-power],
        round(avg([phase3-volt]), 0) as [phase3-volt],
        round(avg([phase3-curr]), 0) as [phase3-curr],
        round(avg([phase3-power]), 0) as [phase3-power],
        round(avg([calculatedPower]), 0) as [calculatedPower],
        count(*) as cntMeasurements
    from ctea5 a
    group by a.TimeDate15m
    union
    select a.station,
        a.TimeDate15m as [timestamp],
        round(avg([activePower-W]), 0) as [activePower-W],
        round(avg([phase1-volt]), 0) as [phase1-volt],
        round(avg([phase1-curr]), 0) as [phase1-curr],
        round(avg([phase1-power]), 0) as [phase1-power],
        round(avg([phase2-volt]), 0) as [phase2-volt],
        round(avg([phase2-curr]), 0) as [phase2-curr],
        round(avg([phase2-power]), 0) as [phase2-power],
        round(avg([phase3-volt]), 0) as [phase3-volt],
        round(avg([phase3-curr]), 0) as [phase3-curr],
        round(avg([phase3-power]), 0) as [phase3-power],
        round(avg([calculatedPower]), 0) as [calculatedPower],
        count(*) as cntMeasurements
    from ctea6 a
    group by a.TimeDate15m
)
select b.*
from cte0 b
where b.timestamp >= datetime('now', '-8 days')