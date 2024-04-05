from coldtype.test import *

@test((800, 150), rstate=1)
def test_versions_sidecar(r, rs):
    assert rs.renderer.source_reader.config.restart_count == 0
    assert __VERSION__["key"] == "test_color"
    assert len(__VERSIONS__) == 15 # i.e. number of visual tests in this folder