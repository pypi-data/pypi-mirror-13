from collections import OrderedDict
import sys
from importlib import import_module

from paver.easy import task, needs, path, sh, cmdopts, options
from paver.setuputils import setup, find_package_data, install_distutils_tasks
try:
    from base_node_rpc.pavement_base import *
except ImportError:
    pass

sys.path.insert(0, '.')
import version
install_distutils_tasks()

DEFAULT_ARDUINO_BOARDS = ['uno']
PROJECT_PREFIX = [d for d in path('.').dirs()
                  if d.joinpath('Arduino').isdir()
                  and d.name not in ('build', )][0].name
name = PROJECT_PREFIX.replace('_', '-')
package_name = name
rpc_module = import_module(PROJECT_PREFIX)
VERSION = version.getVersion()
URL='http://github.com/wheeler-microfluidics/%s.git' % name
package_name = PROJECT_PREFIX.replace('_', '-')
PROPERTIES = OrderedDict([('package_name', package_name),
                          ('display_name', 'DropBot DX'),
                          ('manufacturer', 'Wheeler Lab'),
                          ('software_version', VERSION),
                          ('url', URL)])
LIB_PROPERTIES = PROPERTIES.copy()
LIB_PROPERTIES.update(OrderedDict([('author', 'Christian Fobel'),
                                   ('author_email', 'christian@fobel.net'),
                                   ('short_description', 'Control firmware and'
                                    ' driver for DropBot DX.'),
                                   ('version', VERSION),
                                   ('long_description', ''),
                                   ('category', 'Communication'),
                                   ('architectures', 'avr')]))

options(
    rpc_module=rpc_module,
    PROPERTIES=PROPERTIES,
    LIB_PROPERTIES=LIB_PROPERTIES,
    base_classes=['BaseNodeSerialHandler',
                  'BaseNodeEeprom',
                  'BaseNodeI2c',
                  'BaseNodeI2cHandler<Handler>',
                  'BaseNodeConfig<ConfigMessage, Address>',
                  'BaseNodeState<StateMessage>'],
    rpc_classes=['dropbot_dx::Node'],
    DEFAULT_ARDUINO_BOARDS=DEFAULT_ARDUINO_BOARDS,
    setup=dict(name=PROJECT_PREFIX.replace('_', '-'),
               version=VERSION,
               description=LIB_PROPERTIES['short_description'],
               author=LIB_PROPERTIES['author'],
               author_email=LIB_PROPERTIES['author_email'],
               url=URL,
               license='GPLv2',
               install_requires=['base_node_rpc>=0.13',
                                 'arduino-servo'],
               include_package_data=True,
               packages=[str(PROJECT_PREFIX)]))
