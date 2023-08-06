from pilot import Pilot
from callback import Callback, ValueCallback, DictCallback

data_small = {
  "type": "person",
  "name": "Kathryn Mcclure",
  "car": {
    "make": "Ford",
    "model": "Taurus"
  },
  "family": [
    {
      "type": "person",
      "name": "Reyes Cameron"
    },
    {
      "type": "person",
      "name": "Edna Mcgee"
    },
    {
      "type": "person",
      "name": "Cervantes Bird"
    },
    {
      "type": "person",
      "name": "Jeri Bowen",
      "nested": {
        "more_nested": {
            "nest": True
        }
      }
    }
  ],
  "friends": [
    {
      "type": "person",
      "name": "Battle Riley"
    },
    {
      "type": "person",
      "name": "Delores Townsend"
    },
    {
      "type": "person",
      "name": "Cain Jimenez"
    }
  ],
  "coworkers": [
    {
      "type": "person",
      "name": "Hutchinson Murray"
    },
    {
      "type": "person",
      "name": "Angelica Olsen"
    },
    {
      "type": "person",
      "name": "Lakisha Howard"
    },
    {
      "type": "person",
      "name": "Joann Bean"
    },
    {
      "type": "person",
      "name": "Serena Rowland"
    }
  ],
  "roommates": [
    {
      "type": "person",
      "name": "Blankenship Ware"
    }
  ],
  "pets": [
    {
      "type": "animal",
      "name": "Palmer"
    },
    {
      "type": "animal",
      "name": "Vivian"
    }
  ]
}

count = 0

def test_types():
    class A(object): pass
    class B(object): pass
    class C(A, B): pass
    object_list = [
        "test",
        u'test',
        1,
        1L,
        1.0,
        [],
        {},
        A(),
        B(),
        C(),
        type("NewClass", (object,), {})(),
        False,
        None
    ]
    def node_check(node):
        assert node.val.__node__.__class__.__name__ is 'Node'
    #cb = Callback(node_check)
    pilot = Pilot(node_check)
    pilot.fly(object_list)
    return 1


def test_tree():
    pilot = Pilot()
    data = pilot.fly(data_small)
    assert len(data.__node__.children()) is 8
    assert data.__node__.is_orphan is True
    family = data['family']
    assert len(family.__node__.parents()) is 1
    assert len(family.__node__.children()) is 4
    for child in family.__node__.children(as_generator=True):
        if 'name' in child.val and child.val['name'] == "Jeri Bowen":
            nest = child.val['nested'].__node__.children()[0].children()[0].val
            assert nest.val is True
            assert len(nest.__node__.ancestors()) is 5
            break
    assert len(data.__node__.descendants()) is 58
    assert len(data.__node__.descendants(filters={'type': 'person'})) is 13
    return 1


def test_dtree():
    return 1

def test_graph():
    return 1

count += test_types()
count += test_tree()
#count += test_dtree()
#count += test_graph()
print "{} test(s) completed successfully.".format(str(count))