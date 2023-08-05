"""
Run this to install.
Modified from https://wiki.python.org/moin/Distutils/Tutorial.
"""

from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.

setup(name = "CompoundPye",
      version = "0.93.1",
      description = "Modelling and simulation framework for neural nets of compound eyes.",
      author = "Ilyas Kuhlemann",
      author_email = "ilyasp.ku@gmail.com",
      url = "https://github.com/ilyasku/CompoundPye",
      #Name the folder where your packages live:
      #(If you have other packages (dirs) or modules (py files) then
      #put them into the package directory - they will be found 
      #recursively.)
      packages = ['CompoundPye',
                  'CompoundPye.executables',
                  'CompoundPye.src',
                  'CompoundPye.src.Analyzer',
                  'CompoundPye.src.Circuits',
                  'CompoundPye.src.Components',
                  'CompoundPye.src.Components.Connections',
                  'CompoundPye.src.ErrorHandling',
                  'CompoundPye.src.Examples',
                  'CompoundPye.src.Graph',
                  'CompoundPye.src.GUI',
                  'CompoundPye.src.OmmatidialMap',
                  'CompoundPye.src.Parser',
                  'CompoundPye.src.Sensors',
                  'CompoundPye.src.Surroundings',
                  'CompoundPye.src.Surroundings.Stimuli'],
      scripts=['CompoundPye/executables/cp_GUI.py',
               'CompoundPye/executables/cp_non_GUI_wrapper.py',
               'CompoundPye/executables/cp_analyze_set_of_simulations.py',
               'CompoundPye/executables/cp_analyze_single_simulation.py'],
      long_description = """Modelling and simulation framework for neural nets of compound eyes.""" ,
      license="Creative Commons Attribution-ShareAlike 4.0 International License"
) 
