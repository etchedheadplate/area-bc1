Use buttons or send period as {number of} {hours or days}. Optionaly, you can set {mm:ss} for hours or {hh:mm} for days in UTC +0, otherwise it will be sent at default time. For example:

Every hour at 4 minutes 20 seconds:
`1 hour 04:20`

Every 9 days at 13 hours 12 minutes:
`9 d 13:12`

Every 5 days at default hours:
`5 days`

Every 2 hours at default minutes:
`2 h`

All time is set in UTC +0 timezone
Default hours and minutes are 19:52

Database update schedule:
 - News data always real-time
 - Market, Fees, CEX ~ 7 mins
 - Network, Pools ~ 3 hrs
 - Lightning, ETFs ~ 1 day
 - Seized ~ 3 days
