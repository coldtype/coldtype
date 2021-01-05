(Make sure to `pip install wheel` and `pip install twine`)

```
rm -rf dist/
python setup.py sdist bdist_wheel
python -m twine upload --repository testpypi dist/* --verbose
pip install --index-url https://test.pypi.org/simple/ coldtype
python -m twine upload dist/* --verbose
```