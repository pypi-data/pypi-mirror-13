MiModD - Identify Mutations from Whole-Genome Sequencing Data
*************************************************************

MiModD is an integrated solution for efficient and user-friendly analysis of 
whole-genome sequencing (WGS) data from laboratory model organisms. 
It enables geneticists to identify and annotate the genetic mutations present 
in an organism and to perform linkage analyses to identify variants responsible 
for mutant phenotypes.

MiModD is designed to enable biologists/geneticists with limited 
bioinformatical knowledge to analyze their genome-wide sequencing data without 
the help of a trained bioinformatician.


Requirements
============

MiModD can be installed under Linux and OS X (10.9-10.11) with minimal software 
requirements and a simple setup procedure. As a standalone package it can be 
used from the command line, but can also be integrated seamlessly and easily 
into any local installation of a Galaxy bioinformatics server providing a 
graphical user interface, database management of results and simple composition 
of analysis steps into workflows.

Hardware
--------

For many use cases MiModD performs very well on standard desktop PCs and 
notebooks. Detailed information on hardware requirements and recommendations is 
available at http://mimodd.readthedocs.org/en/latest/hardware.html.

Software
--------

MiModD requires Python 3.2 or higher. Python 2 is not supported.


Obtaining and installing MiModD
===============================

MiModD is pip-installable via::

  python3 -m pip install MiModD

Once installed successfully, run::

  python3 -m MiModD.config

for basic configuration.

More detailed installation instructions for MiModD, dependencies and 
recommended additional software can be found in the INSTALL file included in 
the source distribution or at 
http://mimodd.readthedocs.org/en/latest/INSTALL.html.


Documentation and help
======================

We have prepared a detailed `online documentation 
<http://mimodd.readthedocs.org/en/latest/>`_ of the package including a tutorial for 
beginners. If you experience problems with any part of MiModD or you think you 
found a bug in the software, the preferred way of letting us and others know is 
through posting to the MiModD user group at 
https://groups.google.com/forum/#!forum/mimodd or via email to 
mimodd@googlegroups.com.


