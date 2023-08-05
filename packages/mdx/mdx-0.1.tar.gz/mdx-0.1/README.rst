
MDX
---

This is a simple library to help building .mdx scripts.
It is composed by:

* A simple syntax module to generate mdx
* Functions to generate mdx sets from lists, .json arrays or prefined .mdx sets
* A writer class and a writer context manager

Installation
============

``pip install mdx``

Usage
=====

.. code-block:: python

  # Usage
  from mdx import syntax as s
  from mdx import MDXSetConstructor, writerContext
  from mdx import loadJson, loadMDX

  toyCodeBuilder = MDXSetConstructor(memberPath="[Products].[ProductName]", comment="Product Codes")
  colorCodeBuilder = MDXSetConstructor(memberPath="[Colors]", comment="Color Codes")

  toys = {
    'dolls' : toyCodeBuilder(codeList=[1,2,3], listName="toy dolls")
  }

  colors = {
    'blue' : colorCodeBuilder(codeList=['blue', 'cyan'], listName="blues")
  }

  # Loads .mdx files in path
  # Each file becomes available as a tuple member with the file name as key
  toys = loadMDX(
    "path/to/toys",
    extraMembers = toys, # Add extra members defined by hand
    toyCodeBuilder
  )

  # Loads .json files in path
  # Each file becomes available as a member of a named tuple with the file name as field
  colors = loadJSON(
    "path/to/colors",
    extraMembers = colors,  # Add extra members defined by hand
    colorCodeBuilder
  )

  # The first two arguments are passed automatically by the context manager
  @measure
  def volume(writer, sets, name, *expressions, **kwargs):

    # Perform some common .mdx operations here...

    writer.write(
      s.createMeasure(s.measureMember(name),
        s.sumExisting('[Measures].[PurchaseCount]', s.intersect(*expressions)
        )
      )
    )

  writer = MDXWriter(name='writer', path='./interestingToys') # by default the path is set on config["OUTPUT_FOLDER"]

  # Putting it all together
  with writerContext((toys, colors), writer) as (measures, config):

    measures(volume)(
      # the writer and set variables are passed to the measure after the arguments
      'volume of interesting toy purchases',
      s.tuple(toys.dolls, colors.blue),
      s.exclude(
        s.tuple(toys.cars, colors.any),
        s.tuple(toys.cars, colors.red),
      )
    )

  # The output will be available at ./interestingToys.mdx

  # Configuration options
  from mdx import config
  config["OUTPUT_FOLDER"] = "./path/to/folder"
  config["LIST_BASE_PATH"] = "./path/to/folder"
  config["TAB_SIZE"] = 2
