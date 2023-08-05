def measure(fn):

  def wrapper(writer, BI, *args, **kwargs):

    return fn(writer, BI, *args, **kwargs)

  wrapper.isMeasure = True

  return wrapper
