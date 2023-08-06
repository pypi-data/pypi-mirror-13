Provenance
==========

For every data derived data object, Fastr records the `Provenance <https://en.wikipedia.org/wiki/Provenance>`_. The :py:class:`SinkNode <fastr.core.node.SinkNode>` write provenance records next to every data object it writes out. The records contain information on what operations were performed to obtain the resulting data object.

W3C Prov
--------

The provenance is recorded using the `W3C Prov Data Model (PROV-DM) <https://www.w3.org/TR/2013/REC-prov-dm-20130430/>`_. Behind the scences we are using the python `prov <https://github.com/trungdong/prov>`_ implementation.

The PROV-DM defines 3 Starting Point Classes and and their relating properties. See :numref:`provo` for a graphic representation of the classes and the relations.

.. _provo:

.. figure:: images/provo.svg
  :width: 600px
  :figclass: align-center

  The three Starting Point classes and the properties that relate them. The diagrams in this document depict Entities as yellow ovals, Activities as blue rectangles, and Agents as orange pentagons. The responsibility properties are shown in pink. [*]_


Implementation
--------------

In the workflow document the provenance classes map to fastr concepts in the following way:

:Agent: Fastr, :ref:`Networks <network>`, :ref:`Tools <tools>`, :ref:`Nodes <node>`
:Activity: :py:class:`Jobs <fastr.execution.job.Job>`
:Entities: Data


Usage
-----
The provenance is stored in ProvDocument objects in pickles. The convenience command line tool ``fastr prov`` can be used to extract the provenance in the `PROV-N <http://www.w3.org/TR/prov-n/>`_ notation and can be serialized to `PROV-JSON <http://www.w3.org/Submission/prov-json/>`_ and `PROV-XML <http://www.w3.org/TR/prov-xml/>`_. The provenance document can also be vizualized using the ``fastr prov`` command line tool.




.. rubric:: Footnotes

.. [*] This picture and caption is taken from http://www.w3.org/TR/prov-o/ . "Copyright © 2011-2013 World Wide Web Consortium, (MIT, ERCIM, Keio, Beihang). http://www.w3.org/Consortium/Legal/2015/doc-license"
