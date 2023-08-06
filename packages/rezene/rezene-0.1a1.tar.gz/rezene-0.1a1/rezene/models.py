import re

from lxml import etree


class Element:
    """
    Base abstraction, simply wraps an etree object
    """

    def __init__(self):
        """
        init is for declaration
        """
        pass

    @classmethod
    def wrap(cls, etree_element: etree.Element):
        """
        use this method if you want to use rezene API's with an existing etree.Element
        """
        newobj = cls()
        newobj._element = etree_element
        return newobj

    @classmethod
    def new(cls, *args, **kwargs):
        """
        use this method if you want to create new usable object rather than making a declaration
        """
        raise NotImplementedError('Implement this method')

    @classmethod
    def parse(self, *args, **kwargs):
        """
        use this method if you want to parse XML from a readable
        """
        raise NotImplementedError('Implement this method')


class TerminalElementMixin:
    _value = None

    def r(self):
        if not self._value:
            self._value = self.format()
        return self._value

    def s(self, new_value):
        self._element.text = new_value

    def format(self):
        raise NotImplementedError('Implement this method.')


class BaseField(Element, TerminalElementMixin):
    """
    A field is defined as a tag that does not contains further tags. To give an example,

    <age>10</age>

    is a field, whereas

    <person>
        <age>10</age>
        <name>Ali</name>
    </person>

    is not a field.
    """
    @classmethod
    def new(cls, tag, value, parent=None):
        if parent is None:
            etree_elem = etree.Element(tag)
        else:
            etree_elem = etree.SubElement(parent, tag)
        etree_elem.text = value

        obj = cls()
        obj._element = etree_elem
        return obj


class IntegerField(BaseField):
    def format(self):
        return int(self._element.text)


class CharField(BaseField):
    def format(self):
        return self._element.text


class AutoField(BaseField):
    def format(self):
        return self._element.text


class ModelMetaclass(type):
    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        declared_fields = {}
        fnames = tuple(attrs.keys())
        for field_name in fnames:
            field_obj = attrs[field_name]
            if isinstance(field_obj, Element):
                declared_fields[field_name] = field_obj
                attrs.pop(field_name)
        return declared_fields

    def __new__(mcs, name, bases, attrs):
        attrs['_declared_fields'] = mcs._get_declared_fields(bases, attrs)
        return super(ModelMetaclass, mcs).__new__(mcs, name, bases, attrs)


class Model(Element, metaclass=ModelMetaclass):
    search_ns = None

    @classmethod
    def new(cls, __parent=None, **subelements):
        if __parent is None:
            element = etree.Element(cls.__name__)
        else:
            element = etree.SubElement(__parent, cls.__name__)

        newobj = cls.wrap(element)

        for key, value in subelements.items():
            field = cls._declared_fields[key]
            setattr(newobj, key, field.new(key, value))

        return newobj

    @classmethod
    def parse(cls, url: str):
        root = etree.parse(url).getroot()
        return cls.wrap(root)

    def ns(self, url: str):
        self.search_ns = url
        return self

    def _get_regex(self, field_name: str):
        if self.search_ns:
            escaped = re.escape(self.search_ns)
            pattern = '^{{{}}}'.format(escaped)
            pattern.replace('{', '\{')
            pattern.replace('}', '\}')
            pattern += field_name + '$'
        else:
            pattern = r'^(\{.+\})?' + field_name + r'$'
        return re.compile(pattern)

    def __getattribute__(self, item):
        try:
            return super().__getattribute__(item)
        except AttributeError as ex:
            original_exception = ex

        regex = self._get_regex(item)

        res = []
        for child in self._element:
            match = regex.match(child.tag)
            if match:
                field = self._declared_fields.get(child.tag, None)
                if field is None:
                    field = AutoField()
                res.append(field.wrap(child))

        self.search_ns = None

        if len(res) == 0:
            raise AttributeError(original_exception)
        elif len(res) == 1:
            return res[0]
        else:
            return res

