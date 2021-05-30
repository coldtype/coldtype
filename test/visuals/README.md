To run a file of tests:
- `coldtype test/test_simplest.py`

To run a single test:
- `coldtype test/test_composer.py -ff test_multiline_fit`

To run all the tests so you can cycle through them:
- `python test/runner.py`

Then you can cycle by adding something like this to your `.coldtype.py` file:

```python
__MIDI__["Launch Control XL"]["note_on"][105] = "prev_test"
__MIDI__["Launch Control XL"]["note_on"][106] = "next_test"
```