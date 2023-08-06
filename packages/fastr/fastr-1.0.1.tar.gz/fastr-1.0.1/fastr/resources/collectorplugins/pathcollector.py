__author__ = 'hachterberg'

import re

import fastr
from fastr import exceptions
from fastr.data import url

# Get the plugin type via the interfaces and not via importing, as this will
# lead to a duplicate plugin that does not match!
PLUGIN_TYPE = fastr.interfaces['FastrInterface'].collectors.plugin_class


class PathCollector(PLUGIN_TYPE):
    """
    The PathCollector plugin for the FastrInterface. This plugin uses the
    location fields to find data on the filesystem. To use this plugin the
    method of the output has to be set to ``path``

    The general working is as follows:

    1. The location field is taken from the output
    2. The substitutions are performed on the location field (see below)
    3. The updated location field will be used as a :ref:`regular expression <python:re-syntax>` filter
    4. The filesystem is scanned for all matching files/directory

    The special substitutions performed on the location use the
    Format Specification Mini-Language :ref:`python:formatspec`.
    The predefined fields that can be used are:

    * ``inputs``, an objet with the input values (use like ``{inputs.image[0]}``)
    * ``outputs``, an object with the output values (use like ``{outputs.result[0]}``)
    * ``special`` which has two subfields:

      * ``special.cardinality``, the index of the current cardinality
      * ``special.extension``, is the extension for the output DataType

    Example use::

      <output ... method="path" location="{output.directory[0]}/TransformParameters.{special.cardinality}.{special.extension}"/>

    Given the output directory ``./nodeid/sampleid/result``, the second sample in the output and
    filetype with a ``txt`` extension, this would be translated into::

      <output ... method="path" location="./nodeid/sampleid/result/TransformParameters.1.txt>

    """
    def __init__(self):
        super(PathCollector, self).__init__()
        self.id = 'path'

    def _collect_results(self, interface, output, result):
        output_data = []
        result.result_data[output.id] = output_data
        location = output.location
        use_cardinality = re.search(r'\{special.cardinality(:.*?)??\}', location) is not None

        if use_cardinality:
            nr = 0

            while True:
                specials, inputs, outputs = interface.get_specials(result.payload, output, nr)

                fastr.log.debug('inputs: {}, outputs: {}, specials: {}'.format(inputs, outputs, specials))
                fastr.log.debug('location: {}'.format(location))
                fastr.log.debug('parsed location: {}'.format(location.format(input=inputs, output=outputs, special=specials)))

                value = location.format(input=inputs, output=outputs, special=specials)
                fastr.log.debug('Searching regexp value {}'.format(value))

                if url.isurl(value):
                    value = fastr.vfs.url_to_path(value)

                pathlist = self._regexp_path(value)

                if len(pathlist) < 1:
                    break

                if len(pathlist) > 1:
                    message = 'Found multiple matches for automatic output using {}'.format(value)
                    fastr.log.error(message)
                    raise exceptions.FastrValueError(message)

                value = pathlist[0]

                fastr.log.debug('Got automatic result: {}'.format(value))
                output_data.append(value)

                nr += 1

            # TODO: Add new cardinality check
            #if output.cardinality is not None and len(output_data) != output.cardinality:
            #    raise exceptions.FastrValueError(('Number of found and expected outputs for {} are not matching!'
            #                                      ' (expected {}, found {}, values {})').format(output.id,
            #                                                                                    output.cardinality,
            #                                                                                    len(output_data),
            #                                                                                    output_data))

        else:
            fastr.log.debug('No cardinality branch!')
            specials, inputs, outputs = interface.get_specials(result.payload, output, '')
            value = location.format(input=inputs, output=outputs, special=specials)
            if url.isurl(value):
                value = fastr.vfs.url_to_path(value)

            pathlist = self._regexp_path(value)

            # TODO: Add new cardinality check
            #if output.cardinality is not None and len(value) != output.cardinality:
            #    raise exceptions.FastrValueError(('Number of found and expected outputs for {} are not matching!'
            #                                      '(expected {}, found values: {})').format(output.id,
            #                                                                                output.cardinality,
            #                                                                                value))

            output_data.extend(pathlist)
