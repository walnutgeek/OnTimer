# encoding: utf-8
"""
OnTimer - running stuff on time

"""
__version__ = '0.1'

import datetime
import pytz

class Bounds:
  def __init__(self, lower, upper):
    self.lower = lower
    self.upper = upper
    self.dim = 1 + upper - lower
    self.allrange = tuple(sorted(set(range(self.lower, self.upper + 1))))
    
  def get_id(self, name): 
    return self.lower + (int(name) - self.lower) % self.dim
  def check(self, n):
      if n < self.lower or n > self.upper:
           raise ValueError("n: %d is not between: %d and %d" % (n,self.lower,self.upper) )

  def parse(self, s):
    if s == '*' :
      return self.allrange
    else:
      if s.find('*') >= 0 :
        raise ValueError(s)
      acc = set()
      for p in s.split(',') :
        r = p.split('-')
        if len(r) == 2:
          acc.update(range(self.get_id(r[0]), self.get_id(r[1]) + 1))
        elif len(r) > 2:
          raise ValueError(p)
        else:
          r = p.split('/')
          if len(r) == 2:
            acc.update(range(self.lower if r[0] == '' else self.get_id(r[0]), self.upper + 1, int(r[1])))
          elif len(r) > 2:
            raise ValueError(p)
          else:
            acc.add(self.get_id(r[0]))
      return tuple(sorted(acc))
          
class NamedBounds(Bounds):
  def __init__(self, lower, upper, names):
    Bounds.__init__(self, lower, upper)
    self.names = names
    self.namedict = {x.lower() : i + self.lower for i, x in enumerate(names)}
  
  def get_id(self, name): 
    k = name.lower()
    return self.namedict[k] if k in self.namedict else Bounds.get_id(self, name)

  def get_name(self, id): return self.names[(id - self.lower) % self.dim ]  

cron_fields = (
  ('Seconds', Bounds(0, 59)),
  ('Minutes', Bounds(0, 59)),
  ('Hours', Bounds(0, 23)),
  ('Days', Bounds(1, 31)),
  ('Months', NamedBounds(1, 12, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])),
  ('WeekDays', NamedBounds(0 , 6, ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'])),
  ('Years', Bounds(1000 , 2999)),
  # ('Dates',    DatesBounds(10000101000000 , 29991231235959)) 
)


cron_fields_map = dict(cron_fields)

_SECONDS = 0
_MINUTES = 1
_HOURS = 2
_MONTH_DAY = 3 
_YEAR = 4

class OnState:
  def __init__(self, exp, refs):
    self.exp = exp
    year=refs[_YEAR]
    self.upper_bounds = self.exp.fixed_upper_bounds + (len(self.exp.rules[_MONTH_DAY][year]),)
    self.refs = tuple( self.upper_bounds[i]+x if x < 0 else x for i,x in enumerate(refs))

  def shift(self, compIdx, direction):
    toReset = tuple(self.upper_bounds[i] - 1 if direction == -1 else 0 for i in range(compIdx))
    toCopy = tuple(self.refs[i] for i in range(compIdx + 1, _YEAR + 1))
    return OnState(self.exp, toReset + (self.refs[compIdx] + direction,) + toCopy)
    
  def forward(self):
    for i in range(_YEAR):
      if self.refs[i] + 1 < self.upper_bounds[i]:
        return self.shift(i, 1)
    else:
        return OnState(self.exp, (0, 0, 0, 0, self.exp.forward_year(self.refs[_YEAR] + 1)))

  def back(self):
    for i in range(_YEAR):
      if self.refs[i] > 0 :
        return self.shift(i, -1)
    else:
        return OnState(self.exp, (-1, -1, -1, -1, self.exp.back_year(self.refs[_YEAR] + 1)))
    
  def toDateTime(self):
    y = self.refs[_YEAR]
    md = self.exp.rules[_MONTH_DAY][y][self.refs[_MONTH_DAY]]
    (s, m, h) = (self.exp.rules[i][self.refs[i]] for i in range(_MONTH_DAY))
    return datetime.datetime(y, md[0], md[1], h, m, s)

  def __str__(self):
      return str(self.toDateTime())


class OnExp:
  def __init__(self, s):
    self.s = s
    v = s.split(' ')
    if len(v) < 5:
        raise ValueError("OnTimer expression should have at least 5 fields")
    i = 0
    acc_rules = [(0,), None, None, None, None ]
    if len(v) > 5:
      acc_rules[_SECONDS] = cron_fields_map['Seconds'].parse(v[i])
      i += 1
    acc_rules[_MINUTES] = cron_fields_map['Minutes'].parse(v[i])
    i += 1
    acc_rules[_HOURS] = cron_fields_map['Hours'].parse(v[i])
    i += 1
    days = cron_fields_map['Days'].parse(v[i])
    i += 1
    months = cron_fields_map['Months'].parse(v[i])
    i += 1
    weekdays = cron_fields_map['WeekDays'].parse(v[i])
    i += 1
    acc_rules[_YEAR] = cron_fields_map['Years'].parse(v[i] if len(v) == 7 else '*')
    class month_day_cache(dict):
      def __missing__(self, year):
        cron_fields_map['Years'].check(year)
        dt = datetime.date(year, 1, 1)
        try:
            delta = datetime.timedelta(days=1)
            monthday = []
            while dt.year == year:
              weekday = dt.isoweekday() % 7
              if dt.day in days and dt.month in months and weekday in weekdays:
                monthday.append((dt.month, dt.day))
              dt += delta
            v = tuple(monthday)
            self[year] = v
            return v
        except OverflowError, e:
          import sys
          raise OverflowError, OverflowError( str(e) + ' year=%d dt=%s' % (year,str(dt)) ), sys.exc_info()[2]
      
    acc_rules[_MONTH_DAY] = month_day_cache()
    self.rules = tuple(acc_rules)
    self.fixed_upper_bounds = tuple(len(self.rules[i]) for i in range(_MONTH_DAY))
   
  def state(self, dt):
    if isinstance(dt, basestring):
        dt = datetime.datetime(dt)
    y = dt.year
    md = (dt.month, dt.day)
    state = None
    md_index = None
    cache = self.rules[_MONTH_DAY]
    for i, t in enumerate(cache[y]):
      if t >= md:
        md_index = i
        break
    else:
      md_index = 0
      y = self.forward_year(y + 1)
    state = OnState(self, (0, 0, 0, md_index, y))
    while state.toDateTime() < dt :
        state.forward()
    return state
    
  def forward_year(self, y):
    cache = self.rules[_MONTH_DAY]
    while len(cache[y]) == 0:
      y += 1
    return y

  def back_year(self, y):
    cache = self.rules[_MONTH_DAY]
    while len(cache[y]) == 0:
      y -= 1
    return y


class OnTime:
    def __init__(self, onexp, tz):
        self.onexp = onexp if type(onexp) is OnExp else OnExp(onexp)
        self.tz = tz if isinstance(tz,pytz.tzinfo.BaseTzInfo) else pytz.timezone(tz)

    @staticmethod
    def fromdict(d):
        onexp = d.pop('onexp')
        tz = d.pop('timezone')
        if len(d) > 0:
            raise ValueError("Not supported property: %s" % str(d))
        return OnTime( onexp , tz )
        
    def state(self,dt):
        return self.onexp.state(dt)
    
    def toUtc(self,state):
        return  self.tz.localize(state.toDateTime()).astimezone(pytz.utc)
        
        