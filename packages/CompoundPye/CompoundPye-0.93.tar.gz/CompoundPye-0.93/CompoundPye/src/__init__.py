##@author Ilyas Kuhlemann
#@contact ilyasp.ku@gmail.com
#@date 08.10.14
#
#@mainpage CompoundPye
#
#@section overview Overview
#
#This package provides tools to model the motion detector of insects' visual system. It is designed for easy set-up of columnar structured neural networks, as in arthropods' compound eyes.
#
#@section structure Structure
#
# To get an idea of how to use the module, a good starting point is to run GUI.py in the executables folder
#\n
# BEWARE: No usage example yet, and GUI tool-tips still missing, so setting up simulations without instructions will be hard.


"""
@package CompoundPye.src
This file initializes all sub-packages.

The top level class to use is system.System...
"""



import ErrorHandling as EH

import Components
import Circuits
import Sensors
import Surroundings

import system

#import Plotting

import settings

import Parser

import OmmatidialMap

import Graph

import Analyzer

import GUI
