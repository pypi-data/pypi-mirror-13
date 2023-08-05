import glob, json, codecs
from moretools import decamelize
from collections import namedtuple

from config import config

def MDXSetConstructor(memberPath='', commentTemplate='%s'):

  def MDXSetBuilder(codeList, listName):

    memberFn = lambda c: u"  %s.&[%s]" % (memberPath, c)
    setFn    = lambda x: u",\n".join(map(memberFn, x))
    comment  = commentTemplate % listName
    return u"{\n  // %s \n%s\n}" % (comment, setFn(codeList))

  return MDXSetBuilder

def loadJSON(path, extraMembers={}, mapper=lambda x, y: x):

  items = {}
  path = "%s/%s/*.json" % (config['LIST_BASE_PATH'], path)

  for path in glob.glob(path):
    name = path.split('/')[-1][:-len('.json')]

    for (key, value) in extraMembers.iteritems():
      items[key] = value

    items[name] = mapper(
      json.loads(open(path).read()),
      decamelize(name, ' ').title()
    )

  tupleClass = namedtuple('CodeList', items.keys())
  return tupleClass(*items.values())

def loadMDX(path, extraMembers={}):

  items = {}
  path = "%s/%s/*.mdx" % (config['LIST_BASE_PATH'], path)

  for path in glob.glob(path):
    name = path.split('/')[-1][:-len('.mdx')]

    for (key, value) in extraMembers.iteritems():
      items[key] = value

    items[name] = codecs.open(path, 'r', 'utf-8').read()

  tupleClass = namedtuple('CodeList', items.keys())
  return tupleClass(*items.values())