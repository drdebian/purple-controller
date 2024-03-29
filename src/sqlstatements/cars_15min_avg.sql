with ctea1 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'car1' as vehicle,
        a.*
    from car1 a
),
ctea2 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'car2' as vehicle,
        a.*
    from car2 a
),
ctea3 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'car3' as vehicle,
        a.*
    from car3 a
),
ctea4 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'car4' as vehicle,
        a.*
    from car4 a
),
ctea5 as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        'car5' as vehicle,
        a.*
    from car5 a
),
cte0 as (
    select a.vehicle,
        a.TimeDate15m as [timestamp],
        max([id]) as [id],
        max([status]) as [status],
        round(avg(coalesce([positionLat], 0)), 5) as [positionLat],
        round(avg(coalesce([positionLon], 0)), 5) as [positionLon],
        round(avg(coalesce([distanceLastCharge], 0)), 0) as [distanceLastCharge],
        round(avg(coalesce([avgSpeedLastCharge], 0)), 0) as [avgSpeedLastCharge],
        round(avg(coalesce([stateOfCharge], 0)), 0) as [stateOfCharge],
        count(*) as cntMeasurements
    from ctea1 a
    group by a.TimeDate15m
    union
    select a.vehicle,
        a.TimeDate15m as [timestamp],
        max([id]) as [id],
        max([status]) as [status],
        round(avg(coalesce([positionLat], 0)), 5) as [positionLat],
        round(avg(coalesce([positionLon], 0)), 5) as [positionLon],
        round(avg(coalesce([distanceLastCharge], 0)), 0) as [distanceLastCharge],
        round(avg(coalesce([avgSpeedLastCharge], 0)), 0) as [avgSpeedLastCharge],
        round(avg(coalesce([stateOfCharge], 0)), 0) as [stateOfCharge],
        count(*) as cntMeasurements
    from ctea2 a
    group by a.TimeDate15m
    union
    select a.vehicle,
        a.TimeDate15m as [timestamp],
        max([id]) as [id],
        max([status]) as [status],
        round(avg(coalesce([positionLat], 0)), 5) as [positionLat],
        round(avg(coalesce([positionLon], 0)), 5) as [positionLon],
        round(avg(coalesce([distanceLastCharge], 0)), 0) as [distanceLastCharge],
        round(avg(coalesce([avgSpeedLastCharge], 0)), 0) as [avgSpeedLastCharge],
        round(avg(coalesce([stateOfCharge], 0)), 0) as [stateOfCharge],
        count(*) as cntMeasurements
    from ctea3 a
    group by a.TimeDate15m
    union
    select a.vehicle,
        a.TimeDate15m as [timestamp],
        max([id]) as [id],
        max([status]) as [status],
        round(avg(coalesce([positionLat], 0)), 5) as [positionLat],
        round(avg(coalesce([positionLon], 0)), 5) as [positionLon],
        round(avg(coalesce([distanceLastCharge], 0)), 0) as [distanceLastCharge],
        round(avg(coalesce([avgSpeedLastCharge], 0)), 0) as [avgSpeedLastCharge],
        round(avg(coalesce([stateOfCharge], 0)), 0) as [stateOfCharge],
        count(*) as cntMeasurements
    from ctea4 a
    group by a.TimeDate15m
    union
    select a.vehicle,
        a.TimeDate15m as [timestamp],
        max([id]) as [id],
        max([status]) as [status],
        round(avg(coalesce([positionLat], 0)), 5) as [positionLat],
        round(avg(coalesce([positionLon], 0)), 5) as [positionLon],
        round(avg(coalesce([distanceLastCharge], 0)), 0) as [distanceLastCharge],
        round(avg(coalesce([avgSpeedLastCharge], 0)), 0) as [avgSpeedLastCharge],
        round(avg(coalesce([stateOfCharge], 0)), 0) as [stateOfCharge],
        count(*) as cntMeasurements
    from ctea5 a
    group by a.TimeDate15m
)
select b.*,
    b.stateOfCharge - LAG(b.stateOfCharge, 1, b.stateOfCharge) over (
        partition by b.vehicle
        order by b.vehicle,
            b.timestamp
    ) as chgSOC
from cte0 b
    /* where b.timestamp >= datetime('now', '-8 days') 
     */