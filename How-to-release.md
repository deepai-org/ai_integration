# Pip Release Process

Increase the version number in setup.py .

Then:

```bash
rm -rf dist/
python setup.py sdist bdist_wheel

twine upload dist/*
```
