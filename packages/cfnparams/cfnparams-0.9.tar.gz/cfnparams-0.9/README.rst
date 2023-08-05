|PyPiShield|_
|CircleCIShield|_

cfn-params
==========

A CloudFormation stack parameter utility.

Installation
------------

Install via pip::

    pip install cfnparams

Usage::

    usage: cfn-params [-h] --region REGION [--template TEMPLATE] --output FILENAME
                    --parameters PARAMS [--use-previous-value]
                    [--filter-tag KEYVALUE] [--log-level {DEBUG,INFO,WARN}]
                    [--version] [--resolve-by-name | --resolve-by-tag TAG]

    A CloudFormation stack parameter munging utility.

    optional arguments:
    -h, --help            show this help message and exit
    --region REGION       AWS region
    --template TEMPLATE   JSON template to which the parameters will
                            (potentially) supplied to. If provided, any parameters
                            not declared in the template will be excluded from the
                            output
    --output FILENAME     Filename to write the JSON parameters to
    --parameters PARAMS   A parameter source
    --use-previous-value  Set if UsePreviousValue should be true in the output,
                            defaults to false if not supplied.
    --filter-tag KEYVALUE
                            A tag Key/Value pair which will limit the stack
                            resolution results.
    --log-level {DEBUG,INFO,WARN}
                            Sets the log level
    --version             show program's version number and exit
    --resolve-by-name     Set by default, and will attempt to resolve dependent
                            stacks by the stack name or ID
    --resolve-by-tag TAG  Overrides --resolve-by-name, and will instead use the
                            provided tag name to resolve dependent stacks

    The --parameters argument can be specified multiple times, and can take
    multiple forms:

        1) Key/Value pair supplied directly:

            --parameters ParameterKey=string,ParameterValue=string

        2) A reference to a file containing parameters:

            --parameters file://path/to/file.{py,json}


Motivation
----------

``cfn-params`` overcomes some limitations of the AWS CLI when handling stack paramaters, such as:

* Simultaneously specifying both parameter arguments and parameter files,
  e.g. ``--parameters ParameterKey=foo,ParameterValue=bar --parameters file://params.json``
* Overly verbose JSON format

Features
--------

Parameters can be:

* specified on the CLI
* specified in the AWS CLI JSON format
* specified as Python dictionaries
* resolved from the outputs of other stacks


Parameter Specification
-----------------------

Command Line
^^^^^^^^^^^^

The same format as the AWS CLI is supported, however you must specify each
parameter in its own argument e.g.::

    --parameters ParameterKey=foo,ParameterValue=bar --parameters ParameterKey=baz,ParameterValue=quux


JSON files
^^^^^^^^^^

The same format as the AWS CLI is supported, with the ability to specify as
many input files as you like, e.g.::

    --parameters file://path/to/params.json


Python dictionaries
^^^^^^^^^^^^^^^^^^^

Specified the same way JSON files are, but must have the extension ``.py``::

    --parameters file://path/to/params.py

e.g.::

    {
        # Values must be strings as required by CFN
        'Key': 'Value',

        # All Python builtins are available:
        'FortyTwo': str(6 * 7),
        'MyCommaDelimitedList': ', '.join(['hello', 'world']),
    }



Output parameter resolution
---------------------------

When using the Python parameter format, a local method ``GetOutput(stack, output)`` is available for use, e.g.::

    {
        'foo': GetOutput('other-stack', 'foo'),
    }


Stack lookup and resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a dependent stack is referenced in a parameter, ``cfn-params`` will use the
``DescribeStacks`` API to resolve the parameter from the list of stack outputs.

Two strategies are available:

1. ``--resolve-by-name`` will be used if no strategy specified. It will attempt
   to find a stack with the exact name specified.
2. ``--resolve-by-tag`` will use the value of the tag specified when resolving
   a referenced stack.For example, if you add a ``Name`` tag to your stacks
   and wish to use that for resolution, specify it::

    --resolve-by-tag Name

**Warning**: Resolving by tag is obviously less precise and ``cfn-params`` does not attempt
to tie-break multiple matches, instead returning the first result.

Limiting stack resolution by tag
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``--filter-tag`` argument can be specified multiple times to limit stack
lookup results.
This functionality is useful if you have many stacks with the same name but you
employ tags to differentiate them.

e.g. if you want to only look for stacks in your staging environment::

    --filter-tag Key=Environment,Value=staging




.. |PyPiShield| image:: https://img.shields.io/pypi/v/cfnparams.svg
.. _PyPiShield: https://pypi.python.org/pypi/cfnparams

.. |CircleCIShield| image:: https://circleci.com/gh/expert360/cfn-params.svg?style=shield&circle-token=f392a07f838689452664656015d55a92e55f0b5e
.. _CircleCIShield: https://circleci.com/gh/expert360/cfn-params
