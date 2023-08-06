Fastr Resource File Formats
===========================

This chapter describes the various files fastr uses. The function and format of the files is described allowing the user to configure fastr and add DataTypes and Tools.

.. _config-file:

Config file
-----------

Fastr reads the config files from the following locations by default (in order):

* ``$FASTRDIR/resources/fastr.config``
* ``~/.fastr/fastr.config``

Reading a new config file will prepend or override settings, making the last config file read have the highest priority. All settings have a default value, making config files and all settings within optional.

The config file has the following sections (which will be described in detail):

* ``[system]``, settings regarding the fastr system
* ``[resources]``, setting the path of the fastr resources
* ``[types]``, setting the priority of the DataTypes used in fastr
* ``[server]``, settings regarding the execution server
* ``[mounts]``, setting the mounts for the vfs system

An example config file can be found in ``$FASTRDIR/resources/fastr.config.example``.

``[system]``
^^^^^^^^^^^^

The system section currently only has one setting:

+---------+-------------------------------------------------------------------+---------+
| setting | description                                                       | default |
+=========+===================================================================+=========+
| debug   | enable/disable debugging. Valid values: 0 (disable) or 1 (enable) | 0       |
+---------+-------------------------------------------------------------------+---------+

``[resources]``
^^^^^^^^^^^^^^^

This section is for setting paths to scan for various resources. These paths are scanned recursively for matching files. The earlier path in the list has precendence over the later. The following paths can be set:

+----------------+------------------------------------------------------------+---------------------------------------+
| setting        | description                                                | default                               |
+================+============================================================+=======================================+
| tools          | A list of directories to scan for Tool files               | * ``~/fastr/tools``                   |
|                |                                                            | * ``$FASTR/resources/tools``          |
+----------------+------------------------------------------------------------+---------------------------------------+
| types          | A list of directories to scan for DataType files           | * ``~/fastr/types``                   |
|                |                                                            | * ``$FASTR/resources/types``          |
+----------------+------------------------------------------------------------+---------------------------------------+
| server-plugins | A list of directories to scan for ExecutionInterfaces for  | * ``~/fastr/server-plugins``          |
|                | the fastr exectuion server                                 | * ``$FASTR/resources/server-plugins`` |
+----------------+------------------------------------------------------------+---------------------------------------+
| io-plugins     | A list of directories to scan for IO-plugins for url       | * ``~/fastr/io-plugins``              |
|                | translation for SourceNodes and SinkNodes                  | * ``$FASTR/resources/io-plugins``     |
+----------------+------------------------------------------------------------+---------------------------------------+

``[types]``
^^^^^^^^^^^

The types section currently only has one setting:

+-----------------+-----------------------------------------------------------+---------+
| setting         | description                                               | default |
+=================+===========================================================+=========+
| preferred-types | A list of DataTypes for resolving the type to use in case | [ ]     |
|                 | of ambiguity. The first in the list of the most preffered |         |
+-----------------+-----------------------------------------------------------+---------+

``[server]``
^^^^^^^^^^^^

The section controls the behavior of the execution server.

+-----------------+------------------------------------------------------------+---------------------+
| setting         | description                                                | default             |
+=================+============================================================+=====================+
| name            | The desired name of the server (for client communication)  | localhost           |
+-----------------+------------------------------------------------------------+---------------------+
| port            | The port to listen at                                      | 32787               |
+-----------------+------------------------------------------------------------+---------------------+
| executor-plugin | The ExecutorInterface plugin to use                        | ProcessPoolExecutor |
+-----------------+------------------------------------------------------------+---------------------+
| auto-start      | Wether the fastr instance will automatically start the     | 1                   |
|                 | server when execution of a network is started              |                     |
+-----------------+------------------------------------------------------------+---------------------+


``[mounts]``
^^^^^^^^^^^^

In this section mount points can be specified for the Virtual File System (vfs)
used by fastr. This is simply done by setting ``mountname=/some/local/path``
for each mount.

There are four mounts defined/reserved by the fastr system:

+--------------+----------------------------------------------------------------------------+
| mountname    | path description                                                           |
+==============+============================================================================+
| home         | the users home directory (user expanded ``~/``)                            |
+--------------+----------------------------------------------------------------------------+
| tmp          | System temp dir (unix usually ``/tmp``), acquired by tempfile.gettempdir() |
+--------------+----------------------------------------------------------------------------+
| example_data | ``$FASTRDIR/examples/data``                                                |
+--------------+----------------------------------------------------------------------------+
| apps         | Mount containing the standard fastr apps library, this will be used for    |
|              | fastr marketplace (no default value)                                       |
+--------------+----------------------------------------------------------------------------+

:py:class:`Tool <fastr.core.tool.Tool>` description
---------------------------------------------------

.. _tool-schema:

:py:class:`Tools <fastr.core.tool.Tool>` are the building blocks in the fastr network. To add new
:py:class:`Tools <fastr.core.tool.Tool>` to fastr, XML/json files containing a :py:class:`Tool <fastr.core.tool.Tool>`
definition can be added. These files have the following layout:

+-------------------------------------------------+--------------------------------------------------------------------------------+
| Attribute                                       | Description                                                                    |
+=================================================+================================================================================+
| ``id``                                          | The id of this Tool (used internally in fastr)                                 |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``name``      |                                 | The name of the Tool, for human readability                                    |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``version``   |                                 | The version of the Tool wrapper (not the binary)                               |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``url``       |                                 | The url of the Tool wrapper                                                    |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``authors[]`` |                                 | List of authors of the Tools wrapper                                           |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``name``                        | Name of the author                                                             |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``email``                       | Email address of the author                                                    |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``url``                         | URL of the website of the author                                               |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``tags``      | ``tag[]``                       | List of tags describing the Tool                                               |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``command``   |                                 | Description of the underlying command                                          |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``version``                     | Version of the tool that is wrapped                                            |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``url``                         | Website where the tools that is wrapped can be obtained                        |
|               +---------------+-----------------+--------------------------------------------------------------------------------+
|               | ``targets[]`` |                 | Description of the target binaries/script of this Tool                         |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``os``          | OS targetted (windows, linux, macos or * (for any)                             |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``arch``        | Architecture targetted 32, 64 or * (for any)                                   |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``module``      | Environment module giving access to the Tool                                   |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``location``    | If the module is not found, try using this location to find the Tool           |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``interpreter`` | Interpreter to use to call the ``bin`` with (e.g. bash, python, Rscript)       |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``bin``         | Name of the Tool binary (e.g. toolname, toolname.exe, toolname.py              |
|               +---------------+-----------------+--------------------------------------------------------------------------------+
|               | ``description``                 | Description of the Tool                                                        |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``license``                     | License of the Tool, either full license or a clear name (e.g. LGPL, GPL v2)   |
|               +---------------+-----------------+--------------------------------------------------------------------------------+
|               | ``authors[]`` |                 | List of authors of the Tool (not the wrapper!)                                 |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``name``        | Name of the authors                                                            |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``email``       | Email address of the author                                                    |
|               |               +-----------------+--------------------------------------------------------------------------------+
|               |               | ``url``         | URL of the website of the author                                               | 
+---------------+---------------+-----------------+--------------------------------------------------------------------------------+
| ``inputs[]``  |                                 | List of Inputs that can are accepted by the Tool                               |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``id``                          | ID of the Input                                                                |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``name``                        | Longer name of the Input (more human readable)                                 |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``datatype``                    | The ID of the DataType of the Input [#f1]_                                     |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``enum[]``                      | List of possible values for an EnumType (created on the fly by fastr) [#f1]_   |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``prefix``                      | Commandline prefix of the Input (e.g. --in, -i)                                |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``cardinality``                 | Cardinality of the Input                                                       |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``repeat_prefix``               | Flag indicating if for every value of the Input the prefix is repeated         |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``required``                    | Flag indicating if the input is required                                       |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``nospace``                     | Flag indicating if there is no space between prefix and value (e.g. --in=val)  |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``format``                      | For DataTypes that have multiple representations, indicate which one to use    |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``default``                     | Default value for the Input                                                    |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``description``                 | Long description for an input                                                  |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``outputs[]`` |                                 | List of Outputs that are generated by the Tool (and accessible to fastr)       |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``id``                          | ID of the Output                                                               |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``name``                        | Longer name of the Output (more human readable)                                |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``datatype``                    | The ID of the DataType of the Output [#f1]_                                    |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``enum[]``                      | List of possible values for an EnumType (created on the fly by fastr) [#f1]_   |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``prefix``                      | Commandline prefix of the Output (e.g. --out, -o)                              |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``cardinality``                 | Cardinality of the Output                                                      |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``repeat_prefix``               | Flag indicating if for every value of the Output the prefix is repeated        |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``required``                    | Flag indicating if the input is required                                       |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``nospace``                     | Flag indicating if there is no space between prefix and value (e.g. --out=val) |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``format``                      | For DataTypes that have multiple representations, indicate which one to use    |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``description``                 | Long description for an input                                                  |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``action``                      | Special action (defined per DataType) that needs to be performed before        |
|               |                                 | creating output value (e.g. 'ensure' will make sure an output directory exists)|
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``automatic``                   | Indicate that output doesn't require commandline argument, but is created      |
|               |                                 | automatically by a Tool [#f2]_                                                 |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``method``                      | Method to acquire output value from the Tool can be 'path' or 'stdout' [#f2]_  |
|               +---------------------------------+--------------------------------------------------------------------------------+
|               | ``location``                    | Definition where to an automatically, usage depends on the ``method`` [#f2]_   |
+---------------+---------------------------------+--------------------------------------------------------------------------------+
| ``help``                                        | Help text explaining the use of the Tool                                       |
+-------------------------------------------------+--------------------------------------------------------------------------------+
| ``cite``                                        | Bibtext of the Citation(s) to reference when using this Tool for a publication |
+-------------------------------------------------+--------------------------------------------------------------------------------+

.. rubric:: Footnotes

.. [#f1] ``datatype`` and ``enum`` are conflicting entries, if both specified ``datatype`` has presedence
.. [#f2] More details on defining automatica output are given in [TODO]



