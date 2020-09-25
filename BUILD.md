(Make sure to `pip install wheel` and `pip install twine`)

```
rm -rf dist/
python setup.py sdist bdist_wheel
python -m twine upload dist/* --verbose
```