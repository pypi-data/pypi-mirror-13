User Manual
===========

In this chapter we will discuss the parts of Fastr in more detail. We will give a more complete overview of the system
and describe the more advanced features.

.. _tools:

Tools
-----

The :py:class:`Tools <fastr.core.tool.Tool>` in Fastr are the building blocks of each workflow.
A tool represents a program/script/binary that can be called by Fastr and can be seens as a template.
A :py:class:`Node <fastr.core.node.Node>` can be created based on a :py:class:`Tool <fastr.core.tool.Tool>`.
The Node will be one processing step in a workflow, and the tool defines what the step does.

On the import of Fastr, all available :py:class:`Tools <fastr.core.tool.Tool>` will be loaded in a default
:py:class:`ToolManager <fastr.core.toolmanager.ToolManager>` that can be accessed via ``fastr.toollist``. To get an
overview of the tools in the system, just print the :func:`repr` of the :py:class:`ToolManager <fastr.core.toolmanager.ToolManager>`:

.. code-block:: python

    >>> fastr.toollist
    AddImages                v0.1    :  /home/hachterberg/dev/fastr/fastr/resources/tools/addimages/v1_0/addimages.xml
    AddInt                   v0.1    :  /home/hachterberg/dev/fastr/fastr/resources/tools/addint/v1_0/addint.xml

As you can see it gives the tool id, version and the file from which it was loaded for each tool in the system.
To view the layout of a tool, just print the :func:`repr` of the tool itself.

.. code-block:: python

    >>> fastr.toollist['AddInt']
    Tool AddInt v0.1 (Add two integers)
           Inputs          |       Outputs
    ---------------------------------------------
    left_hand  (Int)       |  result   (Int)
    right_hand (Int)       |

To add a :py:class:`Tool <fastr.core.tool.Tool>` to the system a file should be added to one of the path
in ``fastr.config.tools_path``. The structure of a tool file is described in :ref:`Tool description <tool-schema>`

Create your own tool
~~~~~~~~~~~~~~~~~~~~

There are 4 steps in creating a tool:

1. CREATE FOLDERS. We will call the tool ThrowDie. Create the folder throw_die in the folder fastr-tools. In this folder create another folder called bin.
2. PLACE EXECUTABLE IN CORRECT PLACE. In this example we will use a snippet of executable python code:

   .. code-block:: python

       #!/usr/bin/env python
       import sys
       import random
       import json

       if (len(sys.argv) > 1):
           sides = int(sys.argv[1])
       else:
           sides = 6
       result = [int(random.randint(1, sides ))]

       print('RESULT={}'.format(json.dumps(result)))

   Save this text in a file called ``throw_die.py``

   Place the executable python script in the folder ``throw_die/bin``
3. CREATE AND EDIT XML FILE FOR TOOL.

   Put the following text in file called ``throw_die.xml``.

   .. code-block:: xml

       <tool id="ThrowDie" description="Simulates a throw of a die. Number of sides of the die is provided by user"
             name="throw_die" version="1.0">
         <authors>
           <author name="John Doe" />
         </authors>
         <command version="1.0" >
           <authors>
             <author name="John Doe" url="http://a.b/c" />
           </authors>
           <targets>
             <target arch="*" bin="throw_die.py" interpreter="python" os="*" paths='bin/'/>
           </targets>
           <description>
              throw_die.py number_of_sides
              output = simulated die throw
           </description>
         </command>
         <interface>
           <inputs>
             <input cardinality="1" datatype="Int" description="Number of die sides" id="die_sides" name="die sides" nospace="False" order="0" required="True"/>
            </inputs>
           <outputs>
             <output id="output" name="output value" datatype="Int" automatic="True" cardinality="1" method="json" location="^RESULT=(.*)$" />
           </outputs>
         </interface>
       </tool>

   Put throw_die.xml in the folder example_tool. All tags in the example above are required. The most important tags in this xml are:
   ::
    id      : The id is used in in FASTR to create an instance of your tool, this name will appear in the toollist when you type fastr.toollist.
    targets : This defines where the executables are located and on which platform they are available.
    inputs  : This defines the inputs that you want to be used in FASTR, how FASTR should use them and what data is allowed to be put in there.

   More xml examples can be found in the fastr-tools folder.

4) EDIT CONFIGURATION FILE. Add the line ``[PATH TO LOCATION OF FASTR-TOOLS]/fastr-tools/throw_die/``
   to the the file fast.config (located in .fastr directory) under the ``[resources]`` header.

   For example:

   .. code-block:: ini
 
       [resources]
       # A list of directories to scan for tools, the director added last will be searched first!
       tools:
         /Users/idoe/fastr-tools/image_analysis/tools/
       # A list of directories to scan for types, the director added last will be searched first!
       types:
         /Users/jdoe/fastr-tools/image_analysis/datatypes/

       [mounts]
       # Mounts accessible to fastr virtual file system
       tmp = /tmp/
       home = /Users/jdoe/
       apps = /Users/jdoe/Developer/apps/
       fastr_data = /Users/jdoe/fastr-data/

       [system]
       debug=0

       [types]
       preferred-types:
         NiftiImageFileCompressed

       [web]
       hostname=http://localhost
       port=9000
       # Secret key for save sessions in Flask. Use for instance os.urandom(24)
       secret_key=<<SOMETHING SECURE>>


   You should now have a working tool. To test that everything is ok do the following in python:

   .. code-block:: python

       >>> import fastr
       >>> fastr.toollist

Now a list of available tools should be produced, including the tool throw_die

To test the tool create the script test_throwdie.py:

   .. code-block:: python

    import fastr
    network = fastr.Network()
    source1 = network.create_source(fastr.typelist['Int'], id_='source1')
    sink1 = network.create_sink(fastr.typelist['Int'], id_='sink1')
    throwdie = network.create_node(fastr.toollist['ThrowDie'], id_='throwdie')
    link1 = network.create_link(source1.output, throwdie.inputs['die_sides'])
    link2 = network.create_link(throwdie.outputs['output'], sink1.inputs['input'])
    source_data = {'source1': {'s1': 4, 's2': 5, 's3': 6, 's4': 7}}
    sink_data = {'sink1': 'vfs://tmp/fastr_result_{sample_id}.txt'}
    network.draw_network()
    network.execute(source_data, sink_data)


Call the script from commandline by

 .. code-block:: python

    >>> python test_throwdie.py

An image of the network will be created in the current directory and result files will be put in the tmp directory. The result files are called
``fastr_result_s1.txt``, ``fastr_result_s2.txt``, ``fastr_result_s3.txt``, and ``fastr_result_s4.txt``
  
.. note:: If you have code which is operating system depend you will have to edit the xml file. The following gives and
          example of how the elastix tool does this:

          .. code-block:: xml

              <targets>
                    <target os="windows" arch="*" bin="elastix.exe">
                      <paths>
                        <path type="bin" value="vfs://apps/elastix/4.7/install/" />
                        <path type="lib" value="vfs://apps/elastix/4.7/install/lib" />
                      </paths>
                    </target>
                    <target os="linux" arch="*" modules="elastix/4.7" bin="elastix">
                      <paths>
                        <path type="bin" value="vfs://apps/elastix/4.7/install/" />
                        <path type="lib" value="vfs://apps/elastix/4.7/install/lib" />
                      </paths>
                    </target>
                    <target os="darwin" arch="*" modules="elastix/4.7" bin="elastix">
                      <paths>
                        <path type="bin" value="vfs://apps/elastix/4.7/install/" />
                        <path type="lib" value="vfs://apps/elastix/4.7/install/lib" />
                      </paths>
                    </target>
                 </targets>

``vfs`` is the virtual file system path, more information can be found at
:py:class:`VirtualFileSystem <fastr.core.vfs.VirtualFileSystem>`.


.. _network:

Network
-------

A :py:class:`Network <fastr.core.network.Network>` represented an entire workflow.
It hold all :py:class:`Nodes <fastr.core.node.Node>`, :py:class:`Links <fastr.core.link.Link>` and other information
required to execute the workflow. Networks can be visualized as a number of building blocks (the Nodes) and links
between them:

.. image:: images/network_multi_atlas.*

An empty network is easy to create, all you need is to name it:

.. code-block:: python

    >>> network = fastr.Network(id_="network_name")

The :py:class:`Network <fastr.core.network.Network>` is the main interface to Fastr, from it you can create all elements
to create a workflow. In the following sections the different elements of a
:py:class:`Network <fastr.core.network.Network>` will be described in more detail.


.. _node:

Node
~~~~

:py:class:`Nodes <fastr.core.node.Node>` are the point in the :py:class:`Network <fastr.core.network.Network>` where
the processing happens. A :py:class:`Node <fastr.core.node.Node>` takes the input data and executes jobs as specified
by the underlying :py:class:`Tool <fastr.core.tool.Tool>`. A :py:class:`Nodes <fastr.core.node.Node>` can be created in a two different ways:

.. code-block:: python

    >>> node1 = fastr.Node(tool, id_='node1', parent=network)
    >>> node2 = network.create_node(tool, id_='node2', stepid='step1')

In the first way, we specifically create a :py:class:`Node <fastr.core.node.Node>` object. We pass it an ``id`` and
the ``parent`` network.
If the ``parent`` is ``None`` the ``fastr.curent_network`` will be used.
The :py:class:`Node <fastr.core.node.Node>` constructor will automaticaly add the new node to the ``parent`` network.

.. note:: For a Node, the tool can be given both as the :py:class:`Tool <fastr.core.tool.Tool>` class or the id of the
tool.

The second way, we tell the ``network`` to create a :py:class:`Node <fastr.core.node.Node>`.
The ``network`` will automatically assign itself as the ``parent``.
Optionally you can add define a ``stepid`` for the node which is a logical grouping of
:py:class:`Nodes <fastr.core.node.Node>` that is mostly used for visualization.

A :py:class:`Node <fastr.core.node.Node>` contains :py:class:`Inputs  <fastr.core.inputoutput.Input>` and
:py:class:`Outputs <fastr.core.inputoutput.Output>`. To see the layout of the :py:class:`Node <fastr.core.node.Node>`
one can simply look at the :func:`repr`.

.. code-block:: python

    >>> addint = fastr.Node(fastr.toollist['AddInt'], id_='addint')
    >>> addint
    Node addint (tool: AddInt v1.0)
           Inputs          |       Outputs
    ---------------------------------------------
    left_hand  (Int)       |  result   (Int)
    right_hand (Int)       |

The inputs and outputs are located in mappings with the same name:
    
.. code-block:: python

    >>> addint.inputs
    InputDict([('left_hand', <Input: fastr:///networks/unnamed_network/nodelist/addint/inputs/left_hand>), ('right_hand', <Input: fastr:///networks/unnamed_network/nodelist/addint/inputs/right_hand>)])

    >>> addint.outputs
    OutputDict([('result', Output fastr:///networks/unnamed_network/nodelist/addint/outputs/result)])

The :py:class:`InputDict <fastr.core.node.InputDict>` and :py:class:`OutputDict <fastr.core.node.OutputDict>` are
classes that behave like mappings. The :py:class:`InputDict <fastr.core.node.InputDict>` also facilitaties the linking
shorthand. By assigning an :py:class:`Output <fastr.core.inputoutput.Output>` to an existing key, the
:py:class:`InputDict <fastr.core.node.InputDict>` will create a :py:class:`Link <fastr.core.link.Link>` between the
:py:class:`InputDict <fastr.core.inputoutput.Input>` and :py:class:`Output <fastr.core.inputoutput.Output>`.


.. _source-node:

SourceNode
~~~~~~~~~~

A :py:class:`SourceNode <fastr.core.node.SourceNode>` is a special kind of node that is the start of a workflow.
The :py:class:`SourceNodes <fastr.core.node.SourceNode>` are given data at run-time that fetched via
:py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>`. On create, only the datatype of the data that the
:py:class:`SourceNode <fastr.core.node.SourceNode>` supplied needs to be known. Creating a
:py:class:`SourceNode <fastr.core.node.SourceNode>` is very similar to an ordinary node:

.. code-block:: python

    >>> source1 = fastr.SourceNode('Int', id_='source1')
    >>> source2 = network.create_source(fastr.typelist['Int'], id_='source2', stepid='step1')

In both cases, the source is automatically automaticall assigned to a network.
In the first case to the ``fastr.current_network`` and in the second case to the ``network`` used to call the method.
A :py:class:`SourceNode <fastr.core.node.SourceNode>` only has a single output which has a short-cut access via ``source.output``.

.. note:: For a source or constant node, the datatype can be given both as the :py:class:`BaseDataType <fastr.datatypes.BaseDataType>` class or the id of the datatype.


.. _constant-node:

ConstantNode
~~~~~~~~~~~~

A :py:class:`ConstantNode <fastr.core.node.ConstantNode>` is another special node.
It is a subclass of the :py:class:`SourceNode <fastr.core.node.SourceNode>` and has a similar function.
However, instead of setting the data at run-time, the data of a constant is given at creation and saved in the object.
Creating a :py:class:`ConstantNode <fastr.core.node.ConstantNode>` is similar as creating a source, but with supplying data:

.. code-block:: python

    >>> constant1 = fastr.ConstantNode('Int', [42], id_='constant1')
    >>> constant2 = network.create_constant('Int', [42], id_='constant2', stepid='step1')

Often, when a :py:class:`ConstantNode <fastr.core.node.ConstantNode>` is created, it is created specifically for one input and will not be reused.
In this case there is a shorthand to create and link a constant to an input:

.. code-block:: python
    
    >>> addint.inputs['value1'] = [42]

will create a constant node with the value 42 and create a link between the output and input ``addint.value1``.


.. _sink-node:

SinkNode
~~~~~~~~

The :py:class:`SinkNode <fastr.core.node.SinkNode>` is the counter-part of the source node.
Instead of get data into the workflow, it saves the data resulting from the workflow.
For this a rule has to be given at run-time that determines where to store the data.
The information about how to create such a rule is described at :py:meth:`SinkNode.set_data <fastr.core.node.SinkNode.set_data>`.
At creation time, only the datatype has to be specified:

.. code-block:: python

    >>> sink1 = fastr.Sink('Int', id_='sink1')
    >>> sink2 = network.create_sink(fastr.typelist['Int'], id_='sink2', stepid='step1')


.. _link:

Link
~~~~


:py:class:`Links <fastr.core.link.Link>` indicate how the data flows between :py:class:`Nodes <fastr.core.node.Node>`.
Links can be created explicitly using on of the following:

.. code-block:: python

    >>> link = fastr.Link(node1.outputs['image'], node2.inputs['image'])
    >>> link = network.create_link(node1.outputs['image'], node2.inputs['image'])

or can be create implicitly by assigning an :py:class:`Output <fastr.core.inputoutput.Output>` to an
:py:class:`Input <fastr.core.inputoutput.Input>` in the :py:class:`InputDict <fastr.core.node.InputDict>`.

.. code-block:: python

    # This style of assignment will create a Link similar to above
    >>> node2.inputs['image'] = node1.outputs['image']

Note that a :py:class:`Link <fastr.core.link.Link>` is also create automatically when using the short-hand for the
:py:class:`ConstantNode <fastr.core.node.ConstantNode>`

Data Flow
---------

The data enters the :py:class:`Network <fastr.core.network.Network>` via
:py:class:`SourceNodes <fastr.core.node.SourceNode>`, flows via other :py:class:`Nodes <fastr.core.node.Node>` and
leaves the :py:class:`Network <fastr.core.network.Network>` via :py:class:`SinkNodes <fastr.core.node.SinkNode>`.
The flow between :py:class:`Nodes <fastr.core.node.Node>` goes from an
:py:class:`Output <fastr.core.inputoutput.Output>` via a :py:class:`Link <fastr.core.link.Link>` to an
:py:class:`Input  <fastr.core.inputoutput.Input>`. In the following image it is simple to track the data from
the :py:class:`SourceNodes <fastr.core.node.SourceNode>` at the left to the
:py:class:`SinkNodes <fastr.core.node.SinkNode>` at right side:

.. image:: images/network1.*

Note that the data in Fastr is stored in the :py:class:`Output <fastr.core.inputoutput.Output>` and the
:py:class:`Link <fastr.core.link.Link>` and :py:class:`Input  <fastr.core.inputoutput.Input>` just give access to it
(possible while transforming the data).


Data flow inside a Node
~~~~~~~~~~~~~~~~~~~~~~~

In a :py:class:`Node <fastr.core.node.Node>` all data from the :py:class:`Inputs  <fastr.core.inputoutput.Input>` will
be combined and the jobs will be generated. There are strict rules to how this combination is performed. In the default
case all inputs will be used pair-wise, and if there is only a single value for an input, it it will be considered as
a constant.

To illustrate this we will consider the following :py:class:`Tool <fastr.core.tool.Tool>` (note this is a simplified
version of the real tool):

.. code-block:: python

    >>> fastr.toollist['Elastix']
    Tool Elastix v4.8 (Elastix Registration)
                             Inputs                            |             Outputs
    ----------------------------------------------------------------------------------------------
    fixed_image       (ITKImageFile)                           |  transform (ElastixTransformFile)
    moving_image      (ITKImageFile)                           |
    parameters        (ElastixParameterFile)                   |

Also it is important to know that for this tool (by definition) the cardinality of the ``transform`` :py:class:`Output <fastr.core.inputoutput.Output>`
will match the cardinality of the ``parameters`` :py:class:`Inputs  <fastr.core.inputoutput.Input>`

If we supply a :py:class:`Node <fastr.core.node.Node>` based on this :py:class:`Tool <fastr.core.tool.Tool>` with a
single sample on each :py:class:`Input  <fastr.core.inputoutput.Input>`, there will be one single matching
:py:class:`Output <fastr.core.inputoutput.Output>` sample created:

.. image:: images/flow/flow_simple_one_sample.*

If the cardinality of the ``parameters`` sample would be increased to 2, the resulting ``transform`` sample would also
become 2:

.. image:: images/flow/flow_simple_one_sample_two_cardinality.*

Now if the number of samples on ``fixed_image`` would be increased to 3, the ``moving_image`` and ``parameters``
will be considered constant and be repeated, resulting in 3 ``transform`` samples.

.. image:: images/flow/flow_simple_three_sample.*

Then if the amount of samples for ``moving_image`` is also increased to 3, the ``moving_image`` and ``fixed_image`` will
be used pairwise and the ``parameters`` will be constant.

.. image:: images/flow/flow_simple_three_sample_two_cardinality.*

.. _advanced-flow-node:

Advanced flows in a Node
````````````````````````

Sometimes the default pairwise behaviour is not desirable. For example if you want to test all combinations of certain
input samples. To achieve this we can change the :py:meth:`input_group <fastr.core.inputoutput.Input.input_group>` of
:py:class:`Inputs  <fastr.core.inputoutput.Input>` to set them apart from the rest. By default all
:py:class:`Inputs  <fastr.core.inputoutput.Input>` are assigned to the ``default`` input group. Now let us change that:

.. code-block:: python

    >>> node = network.create_node('Elastix', id_='elastix')
    >>> node.inputs['moving_image'].input_group = 'moving'

This will result in ``moving_image`` to be put in a different input group. Now if we would supply ``fixed_image`` with
3 samples and ``moving_image`` with 4 samples, instead of an error we would get the following result:

.. image:: images/flow/flow_cross_three_sample.*

.. warning:: TODO: Expand this section with the merging dimensions

Data flows in a Link
~~~~~~~~~~~~~~~~~~~~

As mentioned before the data flows from an :py:class:`Output <fastr.core.inputoutput.Output>` to an
:py:class:`Input  <fastr.core.inputoutput.Input>` throuhg a :py:class:`Link <fastr.core.link.Link>`. By default the
:py:class:`Link <fastr.core.link.Link>` passed the data as is, however there are two special directives that change
the shape of the data:

1. Collapsing flow, this collapses certain dimensions from the sample array into the cardinality. As a user you have to
   specify the dimension or tuple of dimensions you want to collapse.

   .. image:: images/flow/flow_collapse.*

   This is useful in situation where you want to use a tool that aggregates over a number of samples (e.g. take a mean
   or sum).

   To achieve this you can set the :py:meth:`collapse <fastr.core.link.Link.collapse>` property of the
   :py:class:`Link <fastr.core.link.Link>` as follows:

   .. code-block:: python

       >>> link.collapse = 'dim1'
       >>> link.collapse = ('dim1', 'dim2')  # In case you want to collapse multiple dimensions

2. Expanding flow, this turns the cardinality into a new dimension. The new dimension will be named after the
   :py:class:`Output <fastr.core.inputoutput.Output>` from which the link originates. It will be in the form of
   ``{nodeid}__{outputid}``

   .. image:: images/flow/flow_expand.*

   This flow directive is useful if you want to split a large sample in multiple smaller samples. This could be because
   processing the whole sample is not feasible because of resource constraints. An example would be splitting a 3D image
   into slices to process separately to avoid high memory use or to achieve parallelism.

   To achieve this you can set the :py:meth:`expand <fastr.core.link.Link.expand>` property of the
   :py:class:`Link <fastr.core.link.Link>` to ``True``:

   .. code-block:: python

       >>> link.expand = True

.. note:: both collapsing and expanding can be used on the same link, it will executes similar to a expand-collapse
          sequence, but the newly created expand dimension is ignored in the collapse.

          .. image:: images/flow/flow_expand_collapse.*

          .. code-block:: python

              >>> link.collapse = 'dim1'
              >>> link.expand = True


Data flows in an Input
~~~~~~~~~~~~~~~~~~~~~~

If an :py:class:`Inputs  <fastr.core.inputoutput.Input>` has multiple :py:class:`Links <fastr.core.link.Link>` attached
to it, the data will be combined by concatenating the values for each corresponding sample in the cardinality.

Broadcasting (matching data of different dimensions)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you might want to combine data that does not have the same number of dimensions. As long as all dimensions of
the lower dimensional datasets match a dimension in the higher dimensional dataset, this can be achieved using
*broadcasting*. The term *broadcasting* is borrowed from `NumPy <http://www.numpy.org/>`_ and described as:

    "The term broadcasting describes how numpy treats arrays with different shapes during arithmetic operations.
    Subject to certain constraints, the smaller array is “broadcast” across the larger array so that they have
    compatible shapes."

    -- `NumPy manual on broadcasting <http://docs.scipy.org/doc/numpy-1.10.1/user/basics.broadcasting.html>`_

In fastr it works similar, but to combined different Inputs in an InputGroup. To illustrate broadcasting it is best to
use an example, the following network uses broadcasting in the ``transformix`` Node:

.. image:: images/network_multi_atlas.*

As you can see this visualization prints the dimensions for each Input and Output (e.g. the ``elastix.fixed_image``
Input has dimensions ``[N]``). To explain what happens in more detail, we present an image illustrating the
details for the samples in ``elastix`` and ``transformix``:

.. image:: images/flow/flow_broadcast.*

In the figure the ``moving_image`` (and references to it) are identified with different colors, so they are easy to
track across the different steps.

At the top the Inputs for the ``elastix`` Node are illustrated. Because the input groups a set differently, output
samples are generated for all combinations of ``fixed_image`` and ``moving_image`` (see :ref:`advanced-flow-node` for
details).

In the ``transformix`` Node, we want to combine a list of samples that is related to the ``moving_image`` (it has the
same dimension name and sizes) with the resulting ``transform`` samples from the ``elastix`` Node. As you can see the
sizes of the sample collections do not match (``[N]`` vs ``[N x M]``). This is where *broadcasting* comes into play, it
allows the system to match these related sample collections. Because all the dimensions in ``[N]`` are known in
``[N x M]``, it is possible to match them uniquely. This is done automatically and the result is a new ``[N xM]`` sample
collection. To create a matching sample collections, the samples in the ``transformix.image`` Input are reused as
indicated by the colors.


.. warning:: Note that this might fail when there are data-blocks with non-unique dimension names, as it will be not
             be clear which of the dimensions with identical names should be matched!

DataTypes
---------

In Fastr all data is contained in object of a specific type. The types in Fastr are represented by classes that subclass :py:class:`BaseDataType <fastr.datatypes.BaseDataType>`. There are a few different other classes under :py:class:`BaseDataType <fastr.datatypes.BaseDataType>` that are each a base class for a family of types:

* :py:class:`DataType <fastr.datatypes.DataType>` -- The base class for all types that hold data

  * :py:class:`ValueType <fastr.datatypes.ValueType>` -- The base class for types that contain simple data (e.g. Int, String) that can be represented as a str
  * :py:class:`EnumType <fastr.datatypes.EnumType>` -- The base class for all types that are a choice from a :class:`set` of options
  * :py:class:`URLType <fastr.datatypes.URLType>` -- The base class for all types that have their data stored in files (which are referenced by URL)

* :py:class:`TypeGroup <fastr.datatypes.TypeGroup>` -- The base class for all types that actually represent a group of types

.. figure:: images/datatype_diagram.*

   The relation between the different DataType classes

The types are defined in xml files and created by the :py:class:`DataTypeManager <fastr.core.datatypemanager.DataTypeManager>`.
The :py:class:`DataTypeManager <fastr.core.datatypemanager.DataTypeManager>` acts as a container containing all Fastr types.
It is automatically instantiated as ``fastr.typelist``.
In fastr the created DataTypes classes are also automatically place in the :py:mod:`fastr.datatypes` module once created.

Resolving Datatypes
~~~~~~~~~~~~~~~~~~~
:py:class:`Outputs <fastr.core.inputoutput.Output>` in fastr can have a :py:class:`TypeGroup <fastr.datatypes.TypeGroup>` or a number of :py:class:`DataTypes <fastr.datatypes.DataType>` associated with them. The final :py:class:`DataType <fastr.datatypes.DataType>` used will
depend on the linked :py:class:`Inputs <fastr.core.inputoutput.Input>`. The :py:class:`DataType <fastr.datatypes.DataType>` resolving works as a two-step procedure.

1. All possible :py:class:`DataTypes <fastr.datatypes.DataType>` are determined and considered as *options*.
2. The best possible :py:class:`DataType <fastr.datatypes.DataType>` from *options* is selected for non-automatic Outputs

The *options* are defined as the intersection of the set of possible values for the :py:class:`Output <fastr.core.inputoutput.Output>` and each separate :py:class:`Input <fastr.core.inputoutput.Input>`
connected to the :py:class:`Output <fastr.core.inputoutput.Output>`. Given the resulting *options* there are three scenarios:

* If there are no valid :py:class:`DataTypes <fastr.datatypes.DataType>` (*options* is empty) the result will be None.
* If there is a single valid :py:class:`DataType <fastr.datatypes.DataType>`, then this is automatically the result (even if it is not a preferred :py:class:`DataType <fastr.datatypes.DataType>`).
* If there are multiple valid :py:class:`DataTypes <fastr.datatypes.DataType>`, then the preferred :py:class:`DataTypes <fastr.datatypes.DataType>` are used to resolve conflicts.

There are a number of places where the preferred :py:class:`DataTypes <fastr.datatypes.DataType>` can be set, these are used in the order as given:

1. The *preferred* keyword argument to :py:meth:`match_types <fastr.core.datatypemanager.DataTypeManager.match_types>`
2. The preferred types specified in the :ref:`fastr.config <config-file>`

.. _manual_execution:

Execution
---------

Executing a Network is very simple:

.. code-block:: python

    >>> source_data = {'source_id1': ['val1', 'val2'],
                       'source_id2': {'id3': 'val3', 'id4': 'val4'}}
    >>> sink_data = {'sink_id1': 'vfs://some_output_location/{sample_id}/file.txt'}
    >>> network.execute(source_data, sink_data)

The :py:meth:`Network.execute <fastr.core.network.Network.execute>` method takes a :class:`dict` of source data
and a :class:`dict` sink data as arguments. The dictionaries should have a key for each
:py:class:`SourceNode <fastr.core.node.SourceNode>` or :py:class:`SinkNode <fastr.core.node.SinkNode>`.

TODO: add ``.. figure:: images/execution_layers.*``

The execution of a Network uses a layered model:

* :py:meth:`Network.execute <fastr.core.network.Network.execute>` will analyze the Network and call all Nodes.
* :py:meth:`Node.execute <fastr.core.node.Node.execute>` will create jobs and fill their payload
* :py:func:`execute_job <fastr.execution.executionscript.execute_job>` will execute the job on the execute machine
  and resolve any deferred values (``val://`` urls).
* :py:meth:`Tool.execute <fastr.core.tool.Tool.execute>` will find the correct target and call the interface and if
  required resolve ``vfs://`` urls
* :py:meth:`Interface.execute <fastr.core.interface.Interface.execute>` will actually run the required command(s)

The :py:class:`ExecutionPlugin <fastr.execution.executionpluginmanager.ExecutionPlugin>` will call call
the :py:mod:`executionscript.py <fastr.execution.executionscript>` for each job, passing the job as a
gzipped pickle file. The :py:mod:`executionscript.py <fastr.execution.executionscript>` will resolve deferred values and
then call :py:meth:`Tool.execute <fastr.core.tool.Tool.execute>` which analyses the required target and executes the
underlying :py:class:`Interface <fastr.core.interface.Interface>`. The Interface actually executes the job and collect
 the results. The result is returned (via the Tool) to the :py:mod:`executionscript.py <fastr.execution.executionscript>`.
  There we save the result, provenance and profiling in a new gzipped pickle file. The execution system will use a
   callback to load the data back into the Network.

The selection and settings of the :py:class:`ExecutionPlugin <fastr.execution.executionpluginmanager.ExecutionPlugin>`
are defined in the :ref:`fastr config <config-file>`.

IOPlugins
---------

Sources and sink are used to get data in and out of a :py:class:`Network <fastr.core.network.Network>` during execution.
To make the data retrieval and storage easier, a plugin system was created that selects different plugins based on the
URL scheme used. So for example, a url starting with ``vfs://`` will be handles by the
:py:class:`VirtualFileSystem plugin <fastr.core.vfs.VirtualFileSystem>`. A list of all the
:py:class:`IOPlugins <fastr.core.ioplugin.IOPlugin>` known by the system and their use can
be found at :ref:`IOPlugin Reference <ioplugin-ref>`.
