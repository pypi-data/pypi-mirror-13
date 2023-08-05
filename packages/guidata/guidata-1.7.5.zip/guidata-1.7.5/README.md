# guidata: Automatic GUI generation for easy dataset editing and display with Python

Simple example of ``guidata`` datasets embedded in an application window:

<img src="http://pythonhosted.org/guidata/_images/editgroupbox.png">

See [documentation](http://pythonhosted.org/guidata/) for more details on 
the library and [changelog](CHANGELOG.md) for recent history of changes.

Copyright © 2009-2015 CEA, Pierre Raybaut, licensed under the terms of the 
CECILL License (see ``Licence_CeCILL_V2-en.txt``).


## Overview

Based on the Qt Python binding module PyQt4, ``guidata`` is a Python library 
generating graphical user interfaces for easy dataset editing and display. It 
also provides helpers and application development tools for PyQt4.

Generate GUIs to edit and display all kind of objects:

- integers, floats, strings ;
- ndarrays (NumPy's n-dimensional arrays) ;
- etc.

Application development tools:

- configuration management
- internationalization (``gettext``)
- deployment tools
- HDF5 I/O helpers
- misc. utils


## Dependencies

### Requirements

- Python >=2.6 or Python >=3.2
- PyQt4 4.x (x>=3 ; recommended x>=4) or PyQt5 5.x (x>=5)
- spyderlib >=v2.0.10 (test launcher and array/dictionnary editors)
    
### Optional Python modules

- h5py (HDF5 files I/O)
- cx_Freeze or py2exe (application deployment on Windows platforms)

### Other optional modules

gettext (text translation support)
        
### Recommended modules

guiqwt >= 3.0


## Installation

### From the source package:

```bash
python setup.py install
```
