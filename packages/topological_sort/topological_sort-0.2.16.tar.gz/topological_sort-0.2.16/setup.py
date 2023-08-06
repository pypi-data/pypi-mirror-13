from distutils.core import setup

with open("README") as f:
    README = f.read()


setup(name="topological_sort",
      version="0.2.16",
      license="MIT",
      description="Topological sorting",
      long_description=README,
      author="Ruda Moura",
      author_email="ruda.moura@gmail.com",
      url="http://rudamoura.com/src/tsort/",
      keywords="DAG, partial order, sorting, topological sort",
      classifiers = ["Programming Language :: Python",
                     "License :: OSI Approved :: MIT License",
                     "Topic :: Scientific/Engineering",
                     "Topic :: Utilities",],
      py_modules = ["topological_sort"],
      scripts=["tsort.py"])
