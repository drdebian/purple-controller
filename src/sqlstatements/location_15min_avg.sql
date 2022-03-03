with ctea as (
    select datetime(
            strftime('%Y-%m-%d %H:00:00', a.TimeDate),
            cast(
                cast(strftime('%M', a.TimeDate) * 4 / 60 + 1 as int) * 60 / 4 as string
            ) || ' minutes'
        ) as TimeDate15m,
        a.*
    from location a
),
cte0 as (
    select a.TimeDate15m as [timestamp],
        round(avg([PV-W]), 0) as [PV-W],
        max([Kreisel Arbeitsmodus]) as [Kreisel Arbeitsmodus],
        round(avg([Kreisel-Ladeleistung]), 0) as [Kreisel-Ladeleistung],
        round(avg([Kreisel-Entladeleistung]), 0) as [Kreisel-Entladeleistung],
        round(avg([Kreisel-SOC]), 0) as [Kreisel-SOC],
        count(*) as cntMeasurements
    from ctea a
    group by a.TimeDate15m
)
select b.*,
    b.[Kreisel-SOC]- LAG(b.[Kreisel-SOC], 1, b.[Kreisel-SOC]) over (
        order by b.timestamp
    )  as chgSOC
from cte0 b
    /* where b.timestamp >= datetime('now', '-8 days')
     */