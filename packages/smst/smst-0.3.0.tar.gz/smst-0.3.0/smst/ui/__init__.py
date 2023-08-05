from __future__ import print_function
import os
import sys
import importlib
import pkgutil

_sound_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../sounds')

def demo_sound_path(file_name):
    'locates a demo sound file'
    return os.path.join(_sound_dir, file_name)

# this allow to run an example of each model or transformation
# eg. $ smst-model dftModel

def run_module(parent_module_name):
    def list_modules(parent_module_path):
        return [module_name for (_, module_name, _) in pkgutil.iter_modules(parent_module_path)]

    module = sys.argv[1] if len(sys.argv) > 1 else None
    parent_module = importlib.import_module(parent_module_name)
    modules = [m.replace('_function', '') for m in
        list_modules(parent_module.__path__)
        if m.endswith('_function')]
    if module in modules:
        importlib.import_module('%s.%s_function' % (parent_module_name, module)).main()
    else:
        print('Available modules:')
        for module in modules:
            print('-', module)

def main_model():
    run_module('smst.ui.models')

def main_transformation():
    run_module('smst.ui.transformations')
