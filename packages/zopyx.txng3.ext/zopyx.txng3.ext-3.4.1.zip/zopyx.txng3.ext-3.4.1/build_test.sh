#!/bin/bash

export PATH=\
/opt/buildout.python/bin:\
$PATH:

if [[ "$1" = "python-2.7" ]]
then
    python_version=2.7
fi

virtualenv-$python_version .
bin/python bootstrap.py
bin/buildout
bin/test-jenkins --xml

