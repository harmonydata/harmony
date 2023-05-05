#!/bin/bash
set -eo pipefail
rm -rf package
cd function
pip3 install --target ../package/python -r requirements.txt
# pip3 install --no-dependencies --target ../package/python -e ../../harmony_pypi_package
cd ..
cp -r ../../harmony_pypi_package/build/lib/harmony/ package/python/
