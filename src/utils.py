import sys, importlib

def load_module(name):
    try:
        importlib.import_module("modules."+name)
    except Exception as e:
        print(e)
        sys.exit(-1)

