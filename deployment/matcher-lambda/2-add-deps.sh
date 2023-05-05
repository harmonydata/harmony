rm -rf function/harmony
cp -r ../../harmony_pypi_package/src/harmony/ function/
mkdir -p deps
pip3 install --no-dependencies --target deps/ -r function/requirements.txt
cp -r deps/pydantic function/
cp -r deps/typing_extensions.py function/
cp -r deps/sklearn function/