# Pip Release Process

Increase the version number in setup.py .

Username for twine is "deepai"

Then:

```bash
rm -rf dist/
python setup.py sdist bdist_wheel

twine upload dist/*
```
