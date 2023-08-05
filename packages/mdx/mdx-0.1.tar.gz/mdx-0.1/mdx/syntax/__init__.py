from ..config import config

RATE = u"""iif(
  %s = 0,
  null,
  %s/%s
)
FORMAT_STRING = "#,##0.00 %%;-#,##0.00 %%"
"""

SUM_EXISTING = u"""
SUM(EXISTING(
%s
), %s)
FORMAT_STRING = "#,##0.00"
"""

def op(operator, args, sep="\n", indent=True,
  prefix="", before_op="\n", after_op="\n", before_wrap="(", after_wrap=")"):

  op = u"".join([before_op, operator, after_op])

  q1 = tab(op.join(args)) if indent else op.join(args)

  return u"".join([prefix, before_wrap, sep, q1, sep, after_wrap])

def tab(s):
  return "\n".join([ (" " * config['TAB_SIZE']) + l for l in s.split('\n') ])

def set(*args):
  return op(",", list(args), before_op="", before_wrap="{", after_wrap="}")

def tuple(*args):
  return op(",", list(args), before_op="")

def intersect(*args):
  return op("*", list(args))

def union(*args):
  return op("+", list(args))

def filter(*args):
  return op("", list(args),
    prefix="FILTER",
    sep="",
    before_op=" ",
    after_op="",
    indent=False,
  )

def subtract(*args):
  return op("-", list(args))

def exclude(*args):
  return op(",", list(args), prefix="EXCEPT", before_op="")

def except_(*args):
  return exclude(*args)

def sumExisting(measurement, from_):
  return SUM_EXISTING % (tab(from_), measurement)

def rate(measurement1, measurement2):
  return RATE % (measurement2, measurement1, measurement2)

def measureMember(name, wrapper="[Measures].[%s]"):
  return wrapper % name

def createMeasure(member, mdx):
  return u'WITH MEMBER %s AS %s' % (member, mdx)

def lf(n=1):
  return u'\n' * n

def title(title):
  delimiter = (len(title) + 1) * "-"
  return u"//%s\n// %s\n//%s\n" % (delimiter, title, delimiter)

