--create view location_15min_avg as 

with cte0 as 
(select 
 datetime(strftime('%Y-%m-%d %H:00:00', a.TimeDate), cast(cast(strftime('%M', a.TimeDate)*4/60+1 as int)*60/4 as string)||' minutes') as TimeDate15m
 ,a.*
 from location a
)
select 
a.TimeDate15m as TimeDate
,round(avg([PV-W]),0) as [PV-W]
,max([Kreisel Arbeitsmodus]) as [Kreisel Arbeitsmodus]
,round(avg([Kreisel-Ladeleistung]), 0) as [Kreisel-Ladeleistung]
,round(avg([Kreisel-Entladeleistung]), 0) as [Kreisel-Entladeleistung]
,round(avg([Kreisel-SOC]), 0) as [Kreisel-SOC]
from cte0 a
group by a.TimeDate15m


