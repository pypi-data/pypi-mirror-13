import codecs, config
from contextlib import contextmanager
from collections import namedtuple
from mdx import *

class MDXWriter:

  def __init__(self, name, path=config['OUTPUT_FOLDER']):
    path = "%s/%s.txt" % (path, name)
    self.file = codecs.open(path, "wb", "utf-8")

  def write(self, data):
    self.file.write(data)
    self.file.write(lf())

  def close(self):
    self.file.close()

@contextmanager
def writerContext(BI, writer=None):

  writer = MDXWriter('output') if not writer else writer
  config = {}

  def measures(*measures):

    def definition(*args, **kwargs):
      kwargs = kwargs.copy()
      kwargs.update(config)

      for measure in measures:

        if not hasattr(measure, 'isMeasure'):
          raise Exception(
            '%s is not a valid measure' % measure.__name__
          )

        measure(writer, BI, *args, **kwargs)

      return definition

    return definition

  yield measures, config
  writer.close()




