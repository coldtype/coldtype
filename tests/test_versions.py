from coldtype.test import *

@test((800, 150))
def test_versions_sidecar(r):
    assert __VERSION__["key"] == "test_color"
    assert len(__VERSIONS__) == 13 # i.e. number of visual tests in this folder