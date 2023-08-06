#!/usr/bin/env python
import os
import sys
import textwrap

if hasattr(sys, 'real_prefix'):
    print('[generate_plugins.py] Inside virtual env: {}'.format(sys.prefix))
else:
    print('[generate_plugins.py] Not inside a virtual env!')

# Add the fastr top level directory for importing without an install
#fastr_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
#print('Source fastr from: {}'.format(fastr_dir))
#sys.path = [fastr_dir] + sys.path

import fastr

def generate_plugins(plugin_header, plugin_manager):
    plugin_type = plugin_manager.plugin_class
    plugin_type_name = plugin_type.__name__
    plugin_type_id = plugin_type_name.lower()

    # The initial document
    doc = [plugin_header, None]
    table = []

    # Extract data from all IOPlugins
    print('[generate_plugins.py] Found Plugins: {}'.format(plugin_manager.keys()))
    for scheme, plugin in sorted(plugin_manager.items()):
        plugin_name = type(plugin).__name__
        underline = '^' * len(plugin_name)
        refname = '.. _{}-{}:'.format(plugin_type_id, plugin_name)
        docstring = plugin.__doc__
        if docstring is None:
            docstring = ''

        docstring = textwrap.dedent(docstring)
        table.append((scheme, plugin_name))
        doc.append('{}\n\n{}\n{}\n\n{}\n'.format(refname,
                                                 plugin_name,
                                                 underline,
                                                 docstring.strip()))

    # Create a table with an overview of the IOPlugins
    table = [(x[0], ':ref:`{0} <{1}-{0}>`'.format(x[1], plugin_type_id)) for x in table]

    # This is to define the max in the consitent way, moved around later
    table.append(('scheme', ':py:class:`{name} <{mod}.{name}>`'.format(name=plugin_type_name, mod=plugin_type.__module__ )))

    len_scheme = max(len(x[0]) for x in table)
    len_refer = max(len(x[1]) for x in table)
    
    # Define the header and the footer
    header = [('=' * len_scheme, '=' * len_refer), 
              table[-1],
              ('=' * len_scheme, '=' * len_refer)]
    footer = [('=' * len_scheme, '=' * len_refer)]

    # Construct final table to print
    table = header + table[:-1] + footer
    table = ['{x[0]:<{slen}} {x[1]:<{rlen}}'.format(x=x, slen=len_scheme, rlen=len_refer) for x in table]

    table = '\n'.join(table)
    doc[1] = table + '\n'

    # Join everything together
    doc = '\n'.join(doc)
    filename = os.path.join(os.path.dirname(__file__), 'fastr.ref.{}s.rst'.format(plugin_type_name.lower()))
    print('[generate_plugins.py] Writing {} reference to {} ({})'.format(plugin_type_name, filename, os.path.abspath(filename)))
    with open(filename, 'w') as output:
        output.write(doc)


def generate_all():
    print('[generate_plugins.py] Start generating IOPlugin reference')
    IO_PLUGIN_HEADER = """
.. _ioplugin-ref:
            
IOPlugins Reference
-------------------

:py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` are used for data import
and export for the sources and sinks. The main use of the
:py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` is during execution (see
:ref:`Execution <manual_execution>`). The :py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>`
can be accessed via ``fastr.ioplugins``, but generally there should be no need
for direct interaction with these objects. The use of is mainly via the URL
used to specify source and sink data.

            """
    generate_plugins(IO_PLUGIN_HEADER, fastr.ioplugins)
    print('[generate_plugins.py] Finished generating IOPlugin reference')

    print('[generate_plugins.py] Start generating CollectorPlugin reference')
    COLLECTOR_PLUGIN_HEADER = """
.. _collectorplugin-ref:
            
CollectorPlugin Reference
-------------------

:py:class:`CollectorPlugins <fastr.resources.interfaceplugins.fasterinterface.CollectorPlugin>`
are used for finding and collecting the output data of outputs part of a
:py:class:`FastrInterface <fastr.resources.interfaceplugins.fasterinterface.FasterInterface>`

            """
    generate_plugins(COLLECTOR_PLUGIN_HEADER, fastr.interfaces['FastrInterface'].collectors)
    print('[generate_plugins.py] Finished generating CollectorPlugin reference')


if __name__ == '__main__':
    generate_all()
