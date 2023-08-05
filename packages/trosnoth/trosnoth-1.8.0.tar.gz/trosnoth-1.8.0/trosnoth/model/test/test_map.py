from trosnoth.model.map import MapLayout
from trosnoth.test.helpers import pytest_funcarg__logman

def test_layout_has_correct_number_of_zones(logman):
    map = MapLayout(2, 3)
    assert len(map.zones) == 19
    map = MapLayout(1, 1)
    assert len(map.zones) == 4
    map = MapLayout(1, 2)
    assert len(map.zones) == 7
    
def test_layout_has_correct_size_and_coordinates(logman):
    map = MapLayout(1,1)
    assert map.worldSize == (5120, 1536)
    map = MapLayout(2, 1)
    assert map.worldSize == (8192,2304)
    
def test_zones_have_correct_coordinates(logman):
    map = MapLayout(2, 1)
    for zone in map.zones:
        if zone.id == 0:
            assert zone.pos == (1024, 1152)
        elif zone.id == 1:
            assert zone.pos == (2560, 768)
        elif zone.id == 2:
            assert zone.pos == (2560, 1536)
        elif zone.id == 3:
            assert zone.pos == (4096, 384)
        elif zone.id == 4:
            assert zone.pos == (4096, 1152)
        elif zone.id == 5:
            assert zone.pos == (4096, 1920)
        elif zone.id == 6:
            assert zone.pos == (5632, 768)
        elif zone.id == 7:
            assert zone.pos == (5632, 1536)
        elif zone.id == 8:
            assert zone.pos == (7168, 1152)
            
    map = MapLayout(1, 1)
    for zone in map.zones:
        if zone.id == 0:
            assert zone.pos == (1024, 768)
        elif zone.id == 1:
            assert zone.pos == (2560, 384)
        elif zone.id == 2:
            assert zone.pos == (2560, 1152)
        elif zone.id == 3:
            assert zone.pos == (4096, 768)