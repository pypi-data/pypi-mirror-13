from distutils.core import setup, Extension

jsvm_mod = Extension('jsvm', sources = ['jsvm.c','jsvm_core.c'])

setup(name = "jsvm",
    version = "1.0",
    description = "Virtual Machine Python Extension type",
    ext_modules = [jsvm_mod],
)
