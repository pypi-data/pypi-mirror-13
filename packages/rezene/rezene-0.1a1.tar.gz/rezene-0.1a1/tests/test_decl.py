import unittest

from rezene import models


NS_NS1 = 'http://www.w3.org/2001/XMLSchema-instance'
NS_NS2 = 'http://www.w3.org/2001/XMLSchema'


class Test_Model_1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class MyModel(models.Model):
            field = models.CharField()

        cls.modelobj = MyModel.new(field='value')

    def test_value(self):
        self.assertEqual(self.modelobj.field.r(), 'value')


class Test_Model_2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class MyModel(models.Model):
            Field1 = models.IntegerField()
            Field2 = models.IntegerField()
            Field3 = models.IntegerField()
            Field4 = models.CharField()
            Field5 = models.CharField()

        cls.modelobj = MyModel.parse('etc/basic.xml')

    def test_value(self):
        self.assertEqual(self.modelobj.Field1.r(), 10)
        self.assertEqual(self.modelobj.Field2.r(), 20)
        self.assertEqual(self.modelobj.Field3.r(), 30)
        self.assertEqual(self.modelobj.Field4.r(), 'Kirmizi')
        self.assertEqual(self.modelobj.Field5.r(), '40')


class Test_Model_3(unittest.TestCase):
    def setUp(self):
        self.obj = models.Model.parse('etc/namespace.xml')

    def test_value(self):
        self.assertEqual(self.obj.ns(NS_NS1).Field.r(), '10')
        self.assertEqual(self.obj.ns(NS_NS2).Field.r(), '20')
        self.assertEqual(self.obj.Field2.r(), '30')
        self.assertEqual(self.obj.Field3.r(), 'Eheh')

    def test_multiple(self):
        res = self.obj.Field

        self.assertEqual(len(res), 2)

        self.assertEqual(res[0].r(), '10')
        self.assertEqual(res[1].r(), '20')


class Test_Model_4(unittest.TestCase):
    def setUp(self):
        self.obj = models.Model.parse('etc/multiple.xml')

    def test_value(self):
        res = self.obj.Name

        self.assertEqual(len(res), 4)

        self.assertEqual(res[0].r(), 'Ugur')
        self.assertEqual(res[1].r(), 'Engin')
        self.assertEqual(res[2].r(), 'Serkan')
        self.assertEqual(res[3].r(), 'Yagiz')


class Test_Model_5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Person(models.Model):
            Name = models.CharField()
            Age = models.IntegerField()

        class MyModel(models.Model):
            NestedField1 = Person()
            NestedField2 = Person()

        cls.modelobj = MyModel.parse('etc/nested_diff.xml')

    def test_value(self):
        self.assertEqual(self.modelobj.NestedField1.Name.r(), 'Ugur')
        self.assertEqual(self.modelobj.NestedField1.Age.r(), 10)

        self.assertEqual(self.modelobj.NestedField2.Name.r(), 'Engin')
        self.assertEqual(self.modelobj.NestedField2.Age.r(), 20)


class Test_Model_6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Automobile(models.Model):
            Cost = models.IntegerField()
            Engine = models.CharField()

        class Person(models.Model):
            Name = models.CharField()
            Age = models.IntegerField()
            Car = Automobile()

        class MyModel(models.Model):
            Person1 = Person()
            Person2 = Person()

        cls.modelobj = MyModel.parse('etc/nested_multiple_level.xml')

    def test_value(self):
        modelobj = self.modelobj

        self.assertEqual(modelobj.Person1.Car.Cost.r(), 100)
        self.assertEqual(modelobj.Person1.Name.r(), 'Ugur')
        self.assertEqual(modelobj.Person1.Age.r(), 10)

        self.assertEqual(modelobj.Person2.Car.Cost.r(), 200)
        self.assertEqual(modelobj.Person2.Name.r(), 'Engin')
        self.assertEqual(modelobj.Person2.Age.r(), 20)

