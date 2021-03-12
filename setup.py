from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {'packages': [], 'excludes': [], 'include_files': ["icon.ico"]}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', base=base, target_name='PSControl', icon="icon.ico")
]

setup(name='PSControl',
      version = '1.0',
      description = 'Control EA Powersupply',
      options = {'build_exe': build_options},
      executables = executables,
      )
