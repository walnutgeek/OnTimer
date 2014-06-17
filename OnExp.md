# OnTimer Expression (OnExp)

Defines when scheduled event need to occur.

Space separated set of 5 to 8 fields. 5 fields expression includes all mandatory fielsda and backward compatiple with unix cron expression. 6 fields expression includes seconds, 7 fields - include seconds and year, and 8 - include all fields. 

ATTENTION: W L # syntax is no implemented yet.

|Field Name  | Mandatory |Allowed Values        | Allowed Special Characters |Value if Omitted| Implementation |
|------------|:---------:|----------------------|----------------------------|:--------------:|----------------|
|Seconds     | no        | 0-59                 | * , - /                    | 0              |Bounds          |
|Mins        | yes       | 0-59                 | * , - /                    |                |Bounds          |
|Hours       | yes       | 0-23                 | * , - /                    |                |Bounds          |
|Day of month| yes       | 1-31                 | * , - / W L                |                |Bounds(for now) |
|Month       | yes       | 1-12 or JAN-DEC      | * , - /                    |                |NamedBounds     |
|Day of week | yes       | 0-6,7 or SUN-SAT,SUN | * , - / #                  |                |NamedBounds     |
|Year        | no        | 1900-2999            | * , - /                    | *              |Bounds          |
|Set of dates| no        | YYYYMMDD             | * , -                      | *              |-               |

## Special characters

| Character | Field |Use |
|:---------:|:-----:|----|
| * | any | to select any value. '*' in the minute field means every minute |
| - | any | to specify ranges. For example, "10-12" in the hour field means "the hours between 10 and 12 inclusive" |
| , |  any |to specify list of values. For example, 'MON,WED,FRI' in the day-of-week field means "the days Monday, Wednesday, and Friday". |
| / | any| to specify increments as [start]/[step]. For example, '/15' or '0/15' in the seconds field is the same as '0,15,30,45' and '5/15' same as '5,20,35,50'. |
| W | Day of month | to specify the weekday (Monday-Friday) nearest the given day within the same month |
| L  | Day of month | to specify last day of the month. For example 'L' or '1L' matches 31-Jan, 28-Feb and so forth. 2L means day second day counting from end of the month and matches 30-Jan, 27-Feb .... |
| LW | Day of month | last weekday of the month |
| # | Day of week | to specify the given day of the week number N in the month. For example, the value of MON#3 means "the third Monday of the month. |

## Credit due to unix cron and quartz's crontrigger

Design is inspired by original unix cron and [quart's crontrigger](http://quartz-scheduler.org/documentation/quartz-1.x/tutorials/crontrigger). 

Intention is to be backward compatible with unix cron expressions as much as possible. Please file bugs if you find valid unix cron expression that does 
not work out of the box in OnTimer. 

Quartz's crontrigger expression may need some modifications. OnTimer treats day of the week field differently from Quartz to be comliant with unix. 
Biggest difference is notation of weekday number. If you port expressions you need substract 1 or better use names. For example in Quartz '0 0 6 \* \* 2-6' 
expression means '6 am every work day'. It could be converted to OnExp as '0 0 \* \* 1-5' or better use names like '0 0 6 \* \* Mon-Fri'. I think you should 
use names anyway because it is easier to read.


