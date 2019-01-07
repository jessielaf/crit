sphinx-apidoc -o . ../crit -f
mv modules.rst index.rst
sphinx-build -b html . _build
