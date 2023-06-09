source activate py311
pip install twine
rm -rf dist
python setup.py sdist
twine upload dist/*
