Introduction
============

Fastr is a system for creating workflows for automated processing of large scale data. A processing workflow might also be called a processing pipeline, however we feel that a pipeline suggests a linear flow of data. Fastr is designed to handle complex flows of data, so we prefer to use the term network. We see the workflow a network of processing tool, through which the data will flow.

The original authors worked in a medical image analysis group at Erasmus MC. There they often had to run analysis that used multiple programs written in different languages. Every time a experiment was set up, the programs had to be glued together by scripts (often in bash or python).

At some point the authors got fed up by doing these things again and again, and so decided to create a flexible, powerful scripting base to create these scripts easily. The idea evolved to a framework in which the building blocks could be defined in XML and the networks could be constructed in very simple scripts (similar to creating a GUI).

This is how development on Fastr started. We hope te release a first version soon.

Philosophy
----------

Researchers spend a lot of time processing data. In image analysis this often includes using multiple tools in succession and feeding the output of one tool to the next. A significant amount of time is spent either executing these tools by hand or writing scripts to automate this process. This process is time consuming and error-prone. Considering all these tasks are very similar, we want to write one elaborate framework that makes it easy to create pipelines, reduces the risk of errors, generates extensive logs, and guarantees reproducibility.

The Fastr framework is applicable to multiple levels of usage: from a single researcher who wants to design a processing pipeline and needs to get reproducible results for publishing; to applying a consolidated image processing pipeline to a large population imaging study. On all levels of application the pipeline provenance and managed execution of the pipeline enables you to get reliable results.

System overview
---------------

There are a few key requirements for the design of the system:

* Any tool that your computer can run using the command line (without user interaction) should be usable by the system without modifying the tool.
* The creation of a workflow should be simple, conceptual and require no real programming.
* Networks, once created, should be usable by anyone like a simple program. All processing should be done automatically.
* All processing of the network should be logged extensively, allowing for complete reproducibility of the system (guaranteeing data provenance).

Using these requirements we define a few key elements in our system:

- A :py:class:`fastr.Tool` is a definition of any program that can be used as part of a pipeline (e.g. a segmentation tool)
- A :py:class:`fastr.Node` is a single operational step in the workflow. This represents the execution of a :py:class:`fastr.Tool`.
- A :py:class:`fastr.Link` indicates how the data flows between nodes.
- A :py:class:`fastr.Network` is an object containing a collection of :py:class:`fastr.Node` and :py:class:`fastr.Link` that form a workflow.

With these building blocks the creation of a pipeline will boil down to just specifying the steps in the pipeline and the flow of the data between them. For example a simple neuro-imaging pipeline could like like:

.. figure:: images/network2.*

    A simple workflow that registers two images and uses the resulting transform to resample the moving image.

In Fastr this translates to:

- Create a :py:class:`fastr.Network` for your pipeline
- Create a :py:class:`fastr.SourceNode` for the fixed image
- Create a :py:class:`fastr.SourceNode` for the moving image
- Create a :py:class:`fastr.SourceNode` for the registration parameters
- Create a :py:class:`fastr.Node` for the registration (in this case elastix)
- Create a :py:class:`fastr.Node` for the resampling of the image (in this case transformix)
- Create a :py:class:`fastr.SinkNode` for the transformations to save
- Create a :py:class:`fastr.SinkNode` for the transformed images to save
- :py:class:`fastr.Link` the output of fixed image source node to the fixed image input of the registration node
- :py:class:`fastr.Link` the output of moving image source node to the moving image input of the registration node
- :py:class:`fastr.Link` the output of registration parameters source node to the registration parameters input of the registration node
- :py:class:`fastr.Link` the output transform of the registration node to the transform input of the resampling
- :py:class:`fastr.Link` the output transform of the registration node to the input of transformation SinkNode
- :py:class:`fastr.Link` the output image of the resampling node to the input of image SinkNode
- Run the :py:class:`fastr.Network` for subjects X

This might seem like a lot of work for a registration, but the Fastr framework manages all other things, executes the pipeline and builds a complete paper trail of all executed operations. The execution can be on any of the supported execution environments (local, cluster, etc). The data can be imported from and exported to any of the supported data connections (file, XNAT, etc). It is also important to keep in mind that this is a simple example, but for more complex pipelines, managing the workflow with Fastr will be easier and less error-prone than writing your own scripts.
