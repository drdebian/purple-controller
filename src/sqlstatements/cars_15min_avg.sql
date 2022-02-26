-- generate new timestamp of next quarter hour for grouping
-- add vehicle name for grouping
with ctea1 as 
(select 
 datetime(strftime('%Y-%m-%d %H:00:00', a.TimeDate), cast(cast(strftime('%M', a.TimeDate)*4/60+1 as int)*60/4 as string)||' minutes') as TimeDate15m
 ,'car1' as vehicle
 ,a.*
 from car1 a
),
ctea2 as 
(select 
 datetime(strftime('%Y-%m-%d %H:00:00', a.TimeDate), cast(cast(strftime('%M', a.TimeDate)*4/60+1 as int)*60/4 as string)||' minutes') as TimeDate15m
 ,'car2' as vehicle
 ,a.*
 from car2 a
),
ctea3 as 
(select 
 datetime(strftime('%Y-%m-%d %H:00:00', a.TimeDate), cast(cast(strftime('%M', a.TimeDate)*4/60+1 as int)*60/4 as string)||' minutes') as TimeDate15m
 ,'car3' as vehicle
 ,a.*
 from car3 a
),
ctea4 as 
(select 
 datetime(strftime('%Y-%m-%d %H:00:00', a.TimeDate), cast(cast(strftime('%M', a.TimeDate)*4/60+1 as int)*60/4 as string)||' minutes') as TimeDate15m
 ,'car4' as vehicle
 ,a.*
 from car4 a
),
ctea5 as 
(select 
 datetime(strftime('%Y-%m-%d %H:00:00', a.TimeDate), cast(cast(strftime('%M', a.TimeDate)*4/60+1 as int)*60/4 as string)||' minutes') as TimeDate15m
 ,'car5' as vehicle
 ,a.*
 from car5 a
),
ctea6 as 
(select 
 datetime(strftime('%Y-%m-%d %H:00:00', a.TimeDate), cast(cast(strftime('%M', a.TimeDate)*4/60+1 as int)*60/4 as string)||' minutes') as TimeDate15m
 ,'car6' as vehicle
 ,a.*
 from car6 a
)

-- union of all individual cars
-- grouped by vehicle name and timestamp
select
a.vehicle
,a.TimeDate15m as [timestamp]
,max([id]) as [id]
,max([status]) as [status]
,round(avg([positionLat]), 5) as [positionLat]
,round(avg([positionLon]), 5) as [positionLon]
,round(avg([distanceLastCharge]), 0) as [distanceLastCharge]
,round(avg([avgSpeedLastCharge]), 0) as [avgSpeedLastCharge]
,round(avg([stateOfCharge]), 0) as [stateOfCharge]
,round(avg([remainingRange]), 0) as [remainingRange]
,round(avg([remainingEnergy]), 0) as [remainingEnergy]
,count(*) as cntMeasurements
from ctea1 a
group by a.TimeDate15m

union

select
a.vehicle
,a.TimeDate15m as [timestamp]
,max([id]) as [id]
,max([status]) as [status]
,round(avg([positionLat]), 5) as [positionLat]
,round(avg([positionLon]), 5) as [positionLon]
,round(avg([distanceLastCharge]), 0) as [distanceLastCharge]
,round(avg([avgSpeedLastCharge]), 0) as [avgSpeedLastCharge]
,round(avg([stateOfCharge]), 0) as [stateOfCharge]
,round(avg([remainingRange]), 0) as [remainingRange]
,round(avg([remainingEnergy]), 0) as [remainingEnergy]
,count(*) as cntMeasurements
from ctea2 a
group by a.TimeDate15m

union

select
a.vehicle
,a.TimeDate15m as [timestamp]
,max([id]) as [id]
,max([status]) as [status]
,round(avg([positionLat]), 5) as [positionLat]
,round(avg([positionLon]), 5) as [positionLon]
,round(avg([distanceLastCharge]), 0) as [distanceLastCharge]
,round(avg([avgSpeedLastCharge]), 0) as [avgSpeedLastCharge]
,round(avg([stateOfCharge]), 0) as [stateOfCharge]
,round(avg([remainingRange]), 0) as [remainingRange]
,round(avg([remainingEnergy]), 0) as [remainingEnergy]
,count(*) as cntMeasurements
from ctea3 a
group by a.TimeDate15m

union

select
a.vehicle
,a.TimeDate15m as [timestamp]
,max([id]) as [id]
,max([status]) as [status]
,round(avg([positionLat]), 5) as [positionLat]
,round(avg([positionLon]), 5) as [positionLon]
,round(avg([distanceLastCharge]), 0) as [distanceLastCharge]
,round(avg([avgSpeedLastCharge]), 0) as [avgSpeedLastCharge]
,round(avg([stateOfCharge]), 0) as [stateOfCharge]
,round(avg([remainingRange]), 0) as [remainingRange]
,round(avg([remainingEnergy]), 0) as [remainingEnergy]
,count(*) as cntMeasurements
from ctea4 a
group by a.TimeDate15m

union

select
a.vehicle
,a.TimeDate15m as [timestamp]
,max([id]) as [id]
,max([status]) as [status]
,round(avg([positionLat]), 5) as [positionLat]
,round(avg([positionLon]), 5) as [positionLon]
,round(avg([distanceLastCharge]), 0) as [distanceLastCharge]
,round(avg([avgSpeedLastCharge]), 0) as [avgSpeedLastCharge]
,round(avg([stateOfCharge]), 0) as [stateOfCharge]
,round(avg([remainingRange]), 0) as [remainingRange]
,round(avg([remainingEnergy]), 0) as [remainingEnergy]
,count(*) as cntMeasurements
from ctea5 a
group by a.TimeDate15m

union

select
a.vehicle
,a.TimeDate15m as [timestamp]
,max([id]) as [id]
,max([status]) as [status]
,round(avg([positionLat]), 5) as [positionLat]
,round(avg([positionLon]), 5) as [positionLon]
,round(avg([distanceLastCharge]), 0) as [distanceLastCharge]
,round(avg([avgSpeedLastCharge]), 0) as [avgSpeedLastCharge]
,round(avg([stateOfCharge]), 0) as [stateOfCharge]
,round(avg([remainingRange]), 0) as [remainingRange]
,round(avg([remainingEnergy]), 0) as [remainingEnergy]
,count(*) as cntMeasurements
from ctea6 a
group by a.TimeDate15m


