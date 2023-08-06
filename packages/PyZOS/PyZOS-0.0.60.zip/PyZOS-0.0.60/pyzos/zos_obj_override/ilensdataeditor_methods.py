# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ilensdataeditor_methods.py
# Purpose:     store custom methods for wrapper class of ILensDataEditor
# Licence:     MIT License
#-------------------------------------------------------------------------------
"""Store custom methods for wrapper class of ILensDataEditor, which defines 
   all properties and methods needed to interact with the Lens Data Editor. 
   This interface can be accessed via the IOpticalSystem interface. 
   name := repr(zos_obj).split()[0].split('.')[-1].lower() + '_methods.py' 
"""
from __future__ import print_function
from __future__ import division
import collections as _co
from win32com.client import CastTo as _CastTo, constants as _constants
from pyzos.zosutils import wrapped_zos_object as _wrapped_zos_object

# Overridden methods
# ------------------

def GetPupil(self):
    """Retrieve pupil data
    """
    pupil_data = _co.namedtuple('pupil_data', ['ZemaxApertureType',
                                               'ApertureValue',
                                               'entrancePupilDiameter',
                                               'entrancePupilPosition',
                                               'exitPupilDiameter',
                                               'exitPupilPosition',
                                               'ApodizationType',
                                               'ApodizationFactor'])
    data = self._ilensdataeditor.GetPupil()
    return pupil_data(*data)


# Overridden properties
# ---------------------


# Extra methods
# -------------
