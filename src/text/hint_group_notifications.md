To setup regular notifications send {command} {number of} {hours or days}. Optionaly, you can set {mm:ss} for hours or {hh:mm} for days in UTC +0, otherwise it will be sent at default time. For example:

News every hour at 4 minutes 20 seconds:
`/notifications news 1 hour 04:20`

Market every 9 days at 13 hours 12 minutes:
`/notifications market 9 d 13:12`

Network every 5 days at default hours:
`/notifications network 5 days`

Lightning every 2 hours at default minutes:
`/notifications lightning 2 h`

All time is set in UTC +0 timezone
Default hours and minutes are 19:52


To manage current notifications send {command} {'manage'}:
`/notifications manage`


To remove notifications send {command} {'remove'} {command index from manage}, for example:

Remove first notification from Manage list:
`/notifications remove 1`

Remove all notifications:
`/notifications remove all`


Database update schedule:
 - News data always current
 - Market, Fees, CEX ~ 7 mins
 - Network, Pools ~ 3 hrs
 - Lightning, ETFs ~ 1 day
 - Seized ~ 3 days
