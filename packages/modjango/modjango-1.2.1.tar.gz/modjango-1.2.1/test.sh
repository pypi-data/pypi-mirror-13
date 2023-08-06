#!/bin/bash

pushd /python_project/modjango > /dev/null;
python3-coverage run --branch  test.py
python3-coverage report --include="*dist-packages/modjango*" --show-missing
python3 /usr/lib/python3/dist-packages/pep8.py . || true
echo
if [ "$1" == "html" ]; then
    echo "producing html report"
    python3-coverage html
else
    echo "not producing html"
fi
popd > /dev/null;


