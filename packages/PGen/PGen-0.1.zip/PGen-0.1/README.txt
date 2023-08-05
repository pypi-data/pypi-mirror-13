===========
PGen
===========

pgen provides generating of data and tests with given format (numbers, string, graphs, etc).
Typical usage often looks like this::

    #!/usr/bin/env python

    from pgen.generator import Generator

    data_description = {
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
    data_seed = 42
    data_count = 3

    generator = Generator(data_description, data_seed)
    generator.write(data_count)
