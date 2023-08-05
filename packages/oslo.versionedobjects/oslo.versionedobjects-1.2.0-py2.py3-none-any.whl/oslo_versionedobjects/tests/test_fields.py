#    Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime

import iso8601
import mock
import netaddr
import six

from oslo_versionedobjects import _utils
from oslo_versionedobjects import base as obj_base
from oslo_versionedobjects import exception
from oslo_versionedobjects import fields
from oslo_versionedobjects import test


class FakeFieldType(fields.FieldType):
    def coerce(self, obj, attr, value):
        return '*%s*' % value

    def to_primitive(self, obj, attr, value):
        return '!%s!' % value

    def from_primitive(self, obj, attr, value):
        return value[1:-1]


class FakeEnum(fields.Enum):
    FROG = "frog"
    PLATYPUS = "platypus"
    ALLIGATOR = "alligator"

    ALL = (FROG, PLATYPUS, ALLIGATOR)

    def __init__(self, **kwargs):
        super(FakeEnum, self).__init__(valid_values=FakeEnum.ALL,
                                       **kwargs)


class FakeEnumAlt(fields.Enum):
    FROG = "frog"
    PLATYPUS = "platypus"
    AARDVARK = "aardvark"

    ALL = (FROG, PLATYPUS, AARDVARK)

    def __init__(self, **kwargs):
        super(FakeEnumAlt, self).__init__(valid_values=FakeEnumAlt.ALL,
                                          **kwargs)


class FakeEnumField(fields.BaseEnumField):
    AUTO_TYPE = FakeEnum()


class FakeEnumAltField(fields.BaseEnumField):
    AUTO_TYPE = FakeEnumAlt()


class TestField(test.TestCase):
    def setUp(self):
        super(TestField, self).setUp()
        self.field = fields.Field(FakeFieldType())
        self.coerce_good_values = [('foo', '*foo*')]
        self.coerce_bad_values = []
        self.to_primitive_values = [('foo', '!foo!')]
        self.from_primitive_values = [('!foo!', 'foo')]

    def test_coerce_good_values(self):
        for in_val, out_val in self.coerce_good_values:
            self.assertEqual(out_val, self.field.coerce('obj', 'attr', in_val))

    def test_coerce_bad_values(self):
        for in_val in self.coerce_bad_values:
            self.assertRaises((TypeError, ValueError),
                              self.field.coerce, 'obj', 'attr', in_val)

    def test_to_primitive(self):
        for in_val, prim_val in self.to_primitive_values:
            self.assertEqual(prim_val, self.field.to_primitive('obj', 'attr',
                                                               in_val))

    def test_from_primitive(self):
        class ObjectLikeThing(object):
            _context = 'context'

        for prim_val, out_val in self.from_primitive_values:
            self.assertEqual(out_val, self.field.from_primitive(
                ObjectLikeThing, 'attr', prim_val))

    def test_stringify(self):
        self.assertEqual('123', self.field.stringify(123))


class TestString(TestField):
    def setUp(self):
        super(TestString, self).setUp()
        self.field = fields.StringField()
        self.coerce_good_values = [
            ('foo', 'foo'), (1, '1'), (1.0, '1.0'), (True, 'True')]
        if six.PY2:
            self.coerce_good_values += [(long(1), '1')]
        self.coerce_bad_values = [None]
        self.to_primitive_values = self.coerce_good_values[0:1]
        self.from_primitive_values = self.coerce_good_values[0:1]

    def test_stringify(self):
        self.assertEqual("'123'", self.field.stringify(123))


class TestSensitiveString(TestString):
    def setUp(self):
        super(TestSensitiveString, self).setUp()
        self.field = fields.SensitiveStringField()

    def test_stringify(self):
        payload = """{'admin_password':'mypassword'}"""
        expected = """'{'admin_password':'***'}'"""
        self.assertEqual(expected, self.field.stringify(payload))


class TestVersionPredicate(TestString):
    def setUp(self):
        super(TestVersionPredicate, self).setUp()
        self.field = fields.VersionPredicateField()
        self.coerce_good_values = [('>=1.0', '>=1.0'),
                                   ('==1.1', '==1.1'),
                                   ('<1.1.0', '<1.1.0')]
        self.coerce_bad_values = ['1', 'foo', '>1', 1.0, '1.0', '=1.0']
        self.to_primitive_values = self.coerce_good_values[0:1]
        self.from_primitive_values = self.coerce_good_values[0:1]


class TestMACAddress(TestField):
    def setUp(self):
        super(TestMACAddress, self).setUp()
        self.field = fields.MACAddressField()
        self.coerce_good_values = [
            ('c6:df:11:a5:c8:5d', 'c6:df:11:a5:c8:5d'),
            ('C6:DF:11:A5:C8:5D', 'c6:df:11:a5:c8:5d'),
            ('c6:df:11:a5:c8:5d', 'c6:df:11:a5:c8:5d'),
            ('C6:DF:11:A5:C8:5D', 'c6:df:11:a5:c8:5d'),
        ]
        self.coerce_bad_values = [
            'C6:DF:11:A5:C8',  # Too short
            'C6:DF:11:A5:C8:5D:D7',  # Too long
            'C6:DF:11:A5:C8:KD',  # Bad octal
        ]
        self.to_primitive_values = self.coerce_good_values[0:1]
        self.from_primitive_values = self.coerce_good_values[0:1]


class TestBaseEnum(TestField):
    def setUp(self):
        super(TestBaseEnum, self).setUp()
        self.field = FakeEnumField()
        self.coerce_good_values = [('frog', 'frog'),
                                   ('platypus', 'platypus'),
                                   ('alligator', 'alligator')]
        self.coerce_bad_values = ['aardvark', 'wookie']
        self.to_primitive_values = self.coerce_good_values[0:1]
        self.from_primitive_values = self.coerce_good_values[0:1]

    def test_stringify(self):
        self.assertEqual("'platypus'", self.field.stringify('platypus'))

    def test_stringify_invalid(self):
        self.assertRaises(ValueError, self.field.stringify, 'aardvark')

    def test_fingerprint(self):
        # Notes(yjiang5): make sure changing valid_value will be detected
        # in test_objects.test_versions
        field1 = FakeEnumField()
        field2 = FakeEnumAltField()
        self.assertNotEqual(str(field1), str(field2))


class TestEnum(TestField):
    def setUp(self):
        super(TestEnum, self).setUp()
        self.field = fields.EnumField(
            valid_values=['foo', 'bar', 1, True])
        self.coerce_good_values = [('foo', 'foo'), (1, '1'), (True, 'True')]
        self.coerce_bad_values = ['boo', 2, False]
        self.to_primitive_values = self.coerce_good_values[0:1]
        self.from_primitive_values = self.coerce_good_values[0:1]

    def test_stringify(self):
        self.assertEqual("'foo'", self.field.stringify('foo'))

    def test_stringify_invalid(self):
        self.assertRaises(ValueError, self.field.stringify, '123')

    def test_fingerprint(self):
        # Notes(yjiang5): make sure changing valid_value will be detected
        # in test_objects.test_versions
        field1 = fields.EnumField(valid_values=['foo', 'bar'])
        field2 = fields.EnumField(valid_values=['foo', 'bar1'])
        self.assertNotEqual(str(field1), str(field2))

    def test_missing_valid_values(self):
        self.assertRaises(exception.EnumRequiresValidValuesError,
                          fields.EnumField, None)

    def test_empty_valid_values(self):
        self.assertRaises(exception.EnumRequiresValidValuesError,
                          fields.EnumField, [])

    def test_non_iterable_valid_values(self):
        self.assertRaises(exception.EnumValidValuesInvalidError,
                          fields.EnumField, True)


class TestInteger(TestField):
    def setUp(self):
        super(TestField, self).setUp()
        self.field = fields.IntegerField()
        self.coerce_good_values = [(1, 1), ('1', 1)]
        self.coerce_bad_values = ['foo', None]
        self.to_primitive_values = self.coerce_good_values[0:1]
        self.from_primitive_values = self.coerce_good_values[0:1]


class TestFloat(TestField):
    def setUp(self):
        super(TestFloat, self).setUp()
        self.field = fields.FloatField()
        self.coerce_good_values = [(1.1, 1.1), ('1.1', 1.1)]
        self.coerce_bad_values = ['foo', None]
        self.to_primitive_values = self.coerce_good_values[0:1]
        self.from_primitive_values = self.coerce_good_values[0:1]


class TestBoolean(TestField):
    def setUp(self):
        super(TestField, self).setUp()
        self.field = fields.BooleanField()
        self.coerce_good_values = [(True, True), (False, False), (1, True),
                                   ('foo', True), (0, False), ('', False)]
        self.coerce_bad_values = []
        self.to_primitive_values = self.coerce_good_values[0:2]
        self.from_primitive_values = self.coerce_good_values[0:2]


class TestFlexibleBoolean(TestField):
    def setUp(self):
        super(TestFlexibleBoolean, self).setUp()
        self.field = fields.FlexibleBooleanField()
        self.coerce_good_values = [(True, True), (False, False),
                                   ("true", True), ("false", False),
                                   ("t", True), ("f", False),
                                   ("yes", True), ("no", False),
                                   ("y", True), ("n", False),
                                   ("on", True), ("off", False),
                                   (1, True), (0, False),
                                   ('frog', False), ('', False)]
        self.coerce_bad_values = []
        self.to_primitive_values = self.coerce_good_values[0:2]
        self.from_primitive_values = self.coerce_good_values[0:2]


class TestDateTime(TestField):
    def setUp(self):
        super(TestDateTime, self).setUp()
        self.dt = datetime.datetime(1955, 11, 5, tzinfo=iso8601.iso8601.Utc())
        self.field = fields.DateTimeField()
        self.coerce_good_values = [(self.dt, self.dt),
                                   (_utils.isotime(self.dt), self.dt)]
        self.coerce_bad_values = [1, 'foo']
        self.to_primitive_values = [(self.dt, _utils.isotime(self.dt))]
        self.from_primitive_values = [(_utils.isotime(self.dt), self.dt)]

    def test_stringify(self):
        self.assertEqual(
            '1955-11-05T18:00:00Z',
            self.field.stringify(
                datetime.datetime(1955, 11, 5, 18, 0, 0,
                                  tzinfo=iso8601.iso8601.Utc())))


class TestDateTimeNoTzinfo(TestField):
    def setUp(self):
        super(TestDateTimeNoTzinfo, self).setUp()
        self.dt = datetime.datetime(1955, 11, 5)
        self.field = fields.DateTimeField(tzinfo_aware=False)
        self.coerce_good_values = [(self.dt, self.dt),
                                   (_utils.isotime(self.dt), self.dt)]
        self.coerce_bad_values = [1, 'foo']
        self.to_primitive_values = [(self.dt, _utils.isotime(self.dt))]
        self.from_primitive_values = [
            (
                _utils.isotime(self.dt),
                self.dt,
            )
        ]

    def test_stringify(self):
        self.assertEqual(
            '1955-11-05T18:00:00Z',
            self.field.stringify(
                datetime.datetime(1955, 11, 5, 18, 0, 0)))


class TestDict(TestField):
    def setUp(self):
        super(TestDict, self).setUp()
        self.field = fields.Field(fields.Dict(FakeFieldType()))
        self.coerce_good_values = [({'foo': 'bar'}, {'foo': '*bar*'}),
                                   ({'foo': 1}, {'foo': '*1*'})]
        self.coerce_bad_values = [{1: 'bar'}, 'foo']
        self.to_primitive_values = [({'foo': 'bar'}, {'foo': '!bar!'})]
        self.from_primitive_values = [({'foo': '!bar!'}, {'foo': 'bar'})]

    def test_stringify(self):
        self.assertEqual("{key=val}", self.field.stringify({'key': 'val'}))


class TestDictOfStrings(TestField):
    def setUp(self):
        super(TestDictOfStrings, self).setUp()
        self.field = fields.DictOfStringsField()
        self.coerce_good_values = [({'foo': 'bar'}, {'foo': 'bar'}),
                                   ({'foo': 1}, {'foo': '1'})]
        self.coerce_bad_values = [{1: 'bar'}, {'foo': None}, 'foo']
        self.to_primitive_values = [({'foo': 'bar'}, {'foo': 'bar'})]
        self.from_primitive_values = [({'foo': 'bar'}, {'foo': 'bar'})]

    def test_stringify(self):
        self.assertEqual("{key='val'}", self.field.stringify({'key': 'val'}))


class TestDictOfIntegers(TestField):
    def setUp(self):
        super(TestDictOfIntegers, self).setUp()
        self.field = fields.DictOfIntegersField()
        self.coerce_good_values = [({'foo': '42'}, {'foo': 42}),
                                   ({'foo': 4.2}, {'foo': 4})]
        self.coerce_bad_values = [{1: 'bar'}, {'foo': 'boo'},
                                  'foo', {'foo': None}]
        self.to_primitive_values = [({'foo': 42}, {'foo': 42})]
        self.from_primitive_values = [({'foo': 42}, {'foo': 42})]

    def test_stringify(self):
        self.assertEqual("{key=42}", self.field.stringify({'key': 42}))


class TestDictOfStringsNone(TestField):
    def setUp(self):
        super(TestDictOfStringsNone, self).setUp()
        self.field = fields.DictOfNullableStringsField()
        self.coerce_good_values = [({'foo': 'bar'}, {'foo': 'bar'}),
                                   ({'foo': 1}, {'foo': '1'}),
                                   ({'foo': None}, {'foo': None})]
        self.coerce_bad_values = [{1: 'bar'}, 'foo']
        self.to_primitive_values = [({'foo': 'bar'}, {'foo': 'bar'})]
        self.from_primitive_values = [({'foo': 'bar'}, {'foo': 'bar'})]

    def test_stringify(self):
        self.assertEqual("{k2=None,key='val'}",
                         self.field.stringify({'k2': None,
                                               'key': 'val'}))


class TestListOfDictOfNullableStringsField(TestField):
    def setUp(self):
        super(TestListOfDictOfNullableStringsField, self).setUp()
        self.field = fields.ListOfDictOfNullableStringsField()
        self.coerce_good_values = [([{'f': 'b', 'f1': 'b1'}, {'f2': 'b2'}],
                                    [{'f': 'b', 'f1': 'b1'}, {'f2': 'b2'}]),
                                   ([{'f': 1}, {'f1': 'b1'}],
                                    [{'f': '1'}, {'f1': 'b1'}]),
                                   ([{'foo': None}], [{'foo': None}])]
        self.coerce_bad_values = [[{1: 'a'}], ['ham', 1], ['eggs']]
        self.to_primitive_values = [([{'f': 'b'}, {'f1': 'b1'}, {'f2': None}],
                                     [{'f': 'b'}, {'f1': 'b1'}, {'f2': None}])]
        self.from_primitive_values = [([{'f': 'b'}, {'f1': 'b1'},
                                        {'f2': None}],
                                       [{'f': 'b'}, {'f1': 'b1'},
                                        {'f2': None}])]

    def test_stringify(self):
        self.assertEqual("[{f=None,f1='b1'},{f2='b2'}]",
                         self.field.stringify(
                             [{'f': None, 'f1': 'b1'}, {'f2': 'b2'}]))


class TestList(TestField):
    def setUp(self):
        super(TestList, self).setUp()
        self.field = fields.Field(fields.List(FakeFieldType()))
        self.coerce_good_values = [(['foo', 'bar'], ['*foo*', '*bar*'])]
        self.coerce_bad_values = ['foo']
        self.to_primitive_values = [(['foo'], ['!foo!'])]
        self.from_primitive_values = [(['!foo!'], ['foo'])]

    def test_stringify(self):
        self.assertEqual('[123]', self.field.stringify([123]))


class TestListOfStrings(TestField):
    def setUp(self):
        super(TestListOfStrings, self).setUp()
        self.field = fields.ListOfStringsField()
        self.coerce_good_values = [(['foo', 'bar'], ['foo', 'bar'])]
        self.coerce_bad_values = ['foo']
        self.to_primitive_values = [(['foo'], ['foo'])]
        self.from_primitive_values = [(['foo'], ['foo'])]

    def test_stringify(self):
        self.assertEqual("['abc']", self.field.stringify(['abc']))


class TestDictOfListOfStrings(TestField):
    def setUp(self):
        super(TestDictOfListOfStrings, self).setUp()
        self.field = fields.DictOfListOfStringsField()
        self.coerce_good_values = [({'foo': ['1', '2']}, {'foo': ['1', '2']}),
                                   ({'foo': [1]}, {'foo': ['1']})]
        self.coerce_bad_values = [{'foo': [None, None]}, 'foo']
        self.to_primitive_values = [({'foo': ['1', '2']}, {'foo': ['1', '2']})]
        self.from_primitive_values = [({'foo': ['1', '2']},
                                       {'foo': ['1', '2']})]

    def test_stringify(self):
        self.assertEqual("{foo=['1','2']}",
                         self.field.stringify({'foo': ['1', '2']}))


class TestListOfEnum(TestField):
    def setUp(self):
        super(TestListOfEnum, self).setUp()
        self.field = fields.ListOfEnumField(valid_values=['foo', 'bar'])
        self.coerce_good_values = [(['foo', 'bar'], ['foo', 'bar'])]
        self.coerce_bad_values = ['foo', ['foo', 'bar1']]
        self.to_primitive_values = [(['foo'], ['foo'])]
        self.from_primitive_values = [(['foo'], ['foo'])]

    def test_stringify(self):
        self.assertEqual("['foo']", self.field.stringify(['foo']))

    def test_stringify_invalid(self):
        self.assertRaises(ValueError, self.field.stringify, '[abc]')

    def test_fingerprint(self):
        # Notes(yjiang5): make sure changing valid_value will be detected
        # in test_objects.test_versions
        field1 = fields.ListOfEnumField(valid_values=['foo', 'bar'])
        field2 = fields.ListOfEnumField(valid_values=['foo', 'bar1'])
        self.assertNotEqual(str(field1), str(field2))


class TestSet(TestField):
    def setUp(self):
        super(TestSet, self).setUp()
        self.field = fields.Field(fields.Set(FakeFieldType()))
        self.coerce_good_values = [(set(['foo', 'bar']),
                                    set(['*foo*', '*bar*']))]
        self.coerce_bad_values = [['foo'], {'foo': 'bar'}]
        self.to_primitive_values = [(set(['foo']), tuple(['!foo!']))]
        self.from_primitive_values = [(tuple(['!foo!']), set(['foo']))]

    def test_stringify(self):
        self.assertEqual('set([123])', self.field.stringify(set([123])))


class TestSetOfIntegers(TestField):
    def setUp(self):
        super(TestSetOfIntegers, self).setUp()
        self.field = fields.SetOfIntegersField()
        self.coerce_good_values = [(set(['1', 2]),
                                    set([1, 2]))]
        self.coerce_bad_values = [set(['foo'])]
        self.to_primitive_values = [(set([1]), tuple([1]))]
        self.from_primitive_values = [(tuple([1]), set([1]))]

    def test_stringify(self):
        self.assertEqual('set([1,2])', self.field.stringify(set([1, 2])))


class TestListOfSetsOfIntegers(TestField):
    def setUp(self):
        super(TestListOfSetsOfIntegers, self).setUp()
        self.field = fields.ListOfSetsOfIntegersField()
        self.coerce_good_values = [([set(['1', 2]), set([3, '4'])],
                                    [set([1, 2]), set([3, 4])])]
        self.coerce_bad_values = [[set(['foo'])]]
        self.to_primitive_values = [([set([1])], [tuple([1])])]
        self.from_primitive_values = [([tuple([1])], [set([1])])]

    def test_stringify(self):
        self.assertEqual('[set([1,2])]', self.field.stringify([set([1, 2])]))


class TestLocalMethods(test.TestCase):
    @mock.patch.object(obj_base.LOG, 'exception')
    def test__make_class_properties_setter_value_error(self, mock_log):
        @obj_base.VersionedObjectRegistry.register
        class AnObject(obj_base.VersionedObject):
            fields = {
                'intfield': fields.IntegerField(),
            }

        self.assertRaises(ValueError, AnObject, intfield='badvalue')
        self.assertFalse(mock_log.called)

    @mock.patch.object(obj_base.LOG, 'exception')
    def test__make_class_properties_setter_setattr_fails(self, mock_log):
        @obj_base.VersionedObjectRegistry.register
        class AnObject(obj_base.VersionedObject):
            fields = {
                'intfield': fields.IntegerField(),
            }

        # We want the setattr() call in _make_class_properties.setter() to
        # raise an exception
        with mock.patch.object(obj_base, '_get_attrname') as mock_attr:
            mock_attr.return_value = '__class__'
            self.assertRaises(TypeError, AnObject, intfield=2)
            mock_attr.assert_called_once_with('intfield')
            mock_log.assert_called_once_with(mock.ANY,
                                             {'attr': 'AnObject.intfield'})


class TestObject(TestField):
    def setUp(self):
        super(TestObject, self).setUp()

        @obj_base.VersionedObjectRegistry.register
        class TestableObject(obj_base.VersionedObject):
            fields = {
                'uuid': fields.StringField(),
                }

            def __eq__(self, value):
                # NOTE(danms): Be rather lax about this equality thing to
                # satisfy the assertEqual() in test_from_primitive(). We
                # just want to make sure the right type of object is re-created
                return value.__class__.__name__ == TestableObject.__name__

        class OtherTestableObject(obj_base.VersionedObject):
            pass

        test_inst = TestableObject()
        self._test_cls = TestableObject
        self.field = fields.Field(fields.Object('TestableObject'))
        self.coerce_good_values = [(test_inst, test_inst)]
        self.coerce_bad_values = [OtherTestableObject(), 1, 'foo']
        self.to_primitive_values = [(test_inst, test_inst.obj_to_primitive())]
        self.from_primitive_values = [(test_inst.obj_to_primitive(),
                                       test_inst),
                                      (test_inst, test_inst)]

    def test_stringify(self):
        obj = self._test_cls(uuid='fake-uuid')
        self.assertEqual('TestableObject(fake-uuid)',
                         self.field.stringify(obj))

    def test_from_primitive(self):
        @obj_base.VersionedObjectRegistry.register
        class TestFakeObject(obj_base.VersionedObject):
            OBJ_PROJECT_NAMESPACE = 'fake-project'

        @obj_base.VersionedObjectRegistry.register
        class TestBar(TestFakeObject, obj_base.ComparableVersionedObject):
            fields = {
                'name': fields.StringField(),
            }

        @obj_base.VersionedObjectRegistry.register
        class TestFoo(TestFakeObject, obj_base.ComparableVersionedObject):
            fields = {
                'name': fields.StringField(),
                'bar': fields.ObjectField('TestBar')
            }

        bar = TestBar(name='bar')
        foo = TestFoo(name='foo', bar=bar)
        from_primitive_values = [(foo.obj_to_primitive(), foo), (foo, foo)]

        for prim_val, out_val in from_primitive_values:
            self.assertEqual(out_val, self.field.from_primitive(
                foo, 'attr', prim_val))

    def test_inheritance(self):
        # We need a whole lot of classes in a hierarchy to
        # test subclass recognition for the Object field
        class TestAnimal(obj_base.VersionedObject):
            pass

        class TestMammal(TestAnimal):
            pass

        class TestReptile(TestAnimal):
            pass

        # We'll use this to create a diamond in the
        # class hierarchy
        class TestPet(TestAnimal):
            pass

        # Non-versioned object mixin
        class TestScary(object):
            pass

        class TestCrocodile(TestReptile, TestPet, TestScary):
            pass

        class TestPig(TestMammal):
            pass

        class TestDog(TestMammal, TestPet):
            pass

        # Some fictional animals
        wolfy = TestDog()  # Terminator-2
        ticktock = TestCrocodile()  # Peter Pan
        babe = TestPig()  # Babe

        # The various classes
        animals = fields.Object('TestAnimal', subclasses=True)
        mammals = fields.Object('TestMammal', subclasses=True)
        reptiles = fields.Object('TestReptile', subclasses=True)
        pets = fields.Object('TestPet', subclasses=True)
        pigs = fields.Object('TestPig', subclasses=True)
        dogs = fields.Object('TestDog', subclasses=True)
        crocs = fields.Object('TestCrocodile', subclasses=True)

        self.assertEqual(["TestDog", "TestMammal", "TestPet",
                          "TestAnimal", "VersionedObject"],
                         fields.Object._get_all_obj_names(wolfy))

        self.assertEqual(["TestCrocodile", "TestReptile", "TestPet",
                          "TestAnimal", "VersionedObject"],
                         fields.Object._get_all_obj_names(ticktock))

        self.assertEqual(["TestPig", "TestMammal",
                          "TestAnimal", "VersionedObject"],
                         fields.Object._get_all_obj_names(babe))

        # Everything is an animal
        self.assertEqual(wolfy, animals.coerce(None, "animal", wolfy))
        self.assertEqual(ticktock, animals.coerce(None, "animal", ticktock))
        self.assertEqual(babe, animals.coerce(None, "animal", babe))

        # crocodiles are not mammals
        self.assertEqual(wolfy, mammals.coerce(None, "animal", wolfy))
        self.assertRaises(ValueError, mammals.coerce, None, "animal", ticktock)
        self.assertEqual(babe, mammals.coerce(None, "animal", babe))

        # dogs and pigs are not reptiles
        self.assertRaises(ValueError, reptiles.coerce, None, "animal", wolfy)
        self.assertEqual(ticktock, reptiles.coerce(None, "animal", ticktock))
        self.assertRaises(ValueError, reptiles.coerce, None, "animal", babe)

        # pigs are not pets, but crocodiles (!) & dogs are
        self.assertEqual(wolfy, pets.coerce(None, "animal", wolfy))
        self.assertEqual(ticktock, pets.coerce(None, "animal", ticktock))
        self.assertRaises(ValueError, pets.coerce, None, "animal", babe)

        # Only dogs are dogs
        self.assertEqual(wolfy, dogs.coerce(None, "animal", wolfy))
        self.assertRaises(ValueError, dogs.coerce, None, "animal", ticktock)
        self.assertRaises(ValueError, dogs.coerce, None, "animal", babe)

        # Only crocs are crocs
        self.assertRaises(ValueError, crocs.coerce, None, "animal", wolfy)
        self.assertEqual(ticktock, crocs.coerce(None, "animal", ticktock))
        self.assertRaises(ValueError, crocs.coerce, None, "animal", babe)

        # Only pigs are pigs
        self.assertRaises(ValueError, pigs.coerce, None, "animal", ticktock)
        self.assertRaises(ValueError, pigs.coerce, None, "animal", wolfy)
        self.assertEqual(babe, pigs.coerce(None, "animal", babe))


class TestIPAddress(TestField):
    def setUp(self):
        super(TestIPAddress, self).setUp()
        self.field = fields.IPAddressField()
        self.coerce_good_values = [('1.2.3.4', netaddr.IPAddress('1.2.3.4')),
                                   ('::1', netaddr.IPAddress('::1')),
                                   (netaddr.IPAddress('::1'),
                                    netaddr.IPAddress('::1'))]
        self.coerce_bad_values = ['1-2', 'foo']
        self.to_primitive_values = [(netaddr.IPAddress('1.2.3.4'), '1.2.3.4'),
                                    (netaddr.IPAddress('::1'), '::1')]
        self.from_primitive_values = [('1.2.3.4',
                                       netaddr.IPAddress('1.2.3.4')),
                                      ('::1',
                                       netaddr.IPAddress('::1'))]


class TestIPAddressV4(TestField):
    def setUp(self):
        super(TestIPAddressV4, self).setUp()
        self.field = fields.IPV4AddressField()
        self.coerce_good_values = [('1.2.3.4', netaddr.IPAddress('1.2.3.4')),
                                   (netaddr.IPAddress('1.2.3.4'),
                                    netaddr.IPAddress('1.2.3.4'))]
        self.coerce_bad_values = ['1-2', 'foo', '::1']
        self.to_primitive_values = [(netaddr.IPAddress('1.2.3.4'), '1.2.3.4')]
        self.from_primitive_values = [('1.2.3.4',
                                       netaddr.IPAddress('1.2.3.4'))]


class TestIPAddressV6(TestField):
    def setUp(self):
        super(TestIPAddressV6, self).setUp()
        self.field = fields.IPV6AddressField()
        self.coerce_good_values = [('::1', netaddr.IPAddress('::1')),
                                   (netaddr.IPAddress('::1'),
                                    netaddr.IPAddress('::1'))]
        self.coerce_bad_values = ['1.2', 'foo', '1.2.3.4']
        self.to_primitive_values = [(netaddr.IPAddress('::1'), '::1')]
        self.from_primitive_values = [('::1',
                                       netaddr.IPAddress('::1'))]


class TestIPNetwork(TestField):
    def setUp(self):
        super(TestIPNetwork, self).setUp()
        self.field = fields.IPNetworkField()
        self.coerce_good_values = [('::1/0', netaddr.IPNetwork('::1/0')),
                                   ('1.2.3.4/24',
                                    netaddr.IPNetwork('1.2.3.4/24')),
                                   (netaddr.IPNetwork('::1/32'),
                                    netaddr.IPNetwork('::1/32'))]
        self.coerce_bad_values = ['foo']
        self.to_primitive_values = [(netaddr.IPNetwork('::1/0'), '::1/0')]
        self.from_primitive_values = [('::1/0',
                                       netaddr.IPNetwork('::1/0'))]


class TestIPV4Network(TestField):
    def setUp(self):
        super(TestIPV4Network, self).setUp()
        self.field = fields.IPV4NetworkField()
        self.coerce_good_values = [('1.2.3.4/24',
                                    netaddr.IPNetwork('1.2.3.4/24'))]
        self.coerce_bad_values = ['foo', '::1/32']
        self.to_primitive_values = [(netaddr.IPNetwork('1.2.3.4/24'),
                                     '1.2.3.4/24')]
        self.from_primitive_values = [('1.2.3.4/24',
                                       netaddr.IPNetwork('1.2.3.4/24'))]


class TestIPV6Network(TestField):
    def setUp(self):
        super(TestIPV6Network, self).setUp()
        self.field = fields.IPV6NetworkField()
        self.coerce_good_values = [('::1/0', netaddr.IPNetwork('::1/0')),
                                   (netaddr.IPNetwork('::1/32'),
                                    netaddr.IPNetwork('::1/32'))]
        self.coerce_bad_values = ['foo', '1.2.3.4/24']
        self.to_primitive_values = [(netaddr.IPNetwork('::1/0'), '::1/0')]
        self.from_primitive_values = [('::1/0',
                                       netaddr.IPNetwork('::1/0'))]
