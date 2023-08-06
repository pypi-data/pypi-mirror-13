from distutils.core import setup, Extension

blake_hash_module = Extension('blake_hash',
                               sources = ['blakemodule.c',
                                          'blake.c',
					  'sphlib/blake.c'],
                               include_dirs=['.', './sphlib'])

setup (name = 'decred_hash',
       version = '1.0.1',
       description = 'Bindings for blake proof of work compatible with Decred.',
       maintainer = 'kefkius',
       maintainer_email = 'kefkius@mail.com',
       url = 'https://github.com/kefkius/decred-hash',
       ext_modules = [blake_hash_module])
