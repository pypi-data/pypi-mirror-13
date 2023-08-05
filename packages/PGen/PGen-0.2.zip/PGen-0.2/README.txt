===========
PGen
===========

pgen provides generating of data and tests with given format (numbers, string, graphs, etc).
Typical usage often looks like this::

    #!/usr/bin/env python

    from pgen.generator import Generator

    data_description = {
        'seed': 42,
        'count': 3,
        'format': {
            'name': 'N',
            'type': 'int',
            'from': 10,
            'to': 100
        },
        'output': {
            'type': 'file',
            'format': 'tests/{0:03d}.dat',
            'start_index': 3
        }
    }

    generator = Generator(data_description)
    generator.write()
