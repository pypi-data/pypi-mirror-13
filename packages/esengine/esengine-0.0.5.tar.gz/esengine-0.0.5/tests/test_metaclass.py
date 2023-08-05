from esengine.bases.metaclass import ModelMetaclass
from esengine.bases.field import BaseField
from esengine.embedded_document import EmbeddedDocument


def test_derived_class_has_fields_attr():
    class NoFields(object):
        __metaclass__ = ModelMetaclass
    assert hasattr(NoFields, '_fields')
    assert len(NoFields._fields) == 0


def test_derived_class_has_correct_field_attr():
    class OneField(object):
        __metaclass__ = ModelMetaclass
        field = BaseField(field_type=int, required=False, multi=False)
    assert hasattr(OneField, '_fields')
    assert len(OneField._fields) == 1
    assert 'field' in OneField._fields
    assert isinstance(OneField._fields['field'], BaseField)
    assert isinstance(OneField.field, BaseField)


def test_has_typefield_if_is_EmbeddedDocument(): # noqa
    obj = ModelMetaclass.__new__(
        ModelMetaclass,
        'name_test',
        (EmbeddedDocument,),
        {}
    )
    assert hasattr(obj, '_type')
    assert getattr(obj, '_type') is obj


def test_id_injected_when_autoid():
    class Base(object):
        __metaclass__ = ModelMetaclass
        _autoid = True

    class Derived(Base):
        pass

    assert hasattr(Derived, 'id')


def test_id_not_injected_when_not_autoid():
    class Base(object):
        __metaclass__ = ModelMetaclass
        _autoid = False

    class Derived(Base):
        pass

    assert not hasattr(Derived, 'id')