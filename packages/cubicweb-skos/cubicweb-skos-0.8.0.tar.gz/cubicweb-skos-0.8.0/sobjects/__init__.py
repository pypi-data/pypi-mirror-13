from cubes.skos import POST_321

if POST_321:
    # use new CW 3.21 dataimport API
    from cubes.skos.sobjects.post321 import *  # noqa
    from cubes.skos.sobjects.post321 import _skos_import_lcsv  # noqa
    from cubes.skos.sobjects.post321 import _skos_import_rdf  # noqa
else:
    from cubes.skos.sobjects.pre321 import *  # noqa
    from cubes.skos.sobjects.pre321 import _skos_import_lcsv  # noqa
    from cubes.skos.sobjects.pre321 import _skos_import_rdf  # noqa

del registration_callback  # noqa
