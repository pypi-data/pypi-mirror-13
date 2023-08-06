websauna.viewconfig
=====================

.. |ci| image:: https://drone.io/bitbucket.org/websauna/websauna.viewconfig/status.png
    :target: https://drone.io/bitbucket.org/websauna/websauna.viewconfig/latest

.. |cov| image:: https://codecov.io/bitbucket/websauna/websauna.viewconfig/coverage.svg?branch=master
    :target: https://codecov.io/bitbucket/websauna/websauna.viewconfig?branch=master

.. |downloads| image:: https://pypip.in/download/websauna.viewconfig/badge.png
    :target: https://pypi.python.org/pypi/websauna.viewconfig/
    :alt: Downloads

.. |latest| image:: https://pypip.in/version/websauna.viewconfig/badge.png
    :target: https://pypi.python.org/pypi/websauna.viewconfig/
    :alt: Latest Version

.. |license| image:: https://pypip.in/license/pyramid_notebook/badge.png
    :target: https://pypi.python.org/pypi/websauna.viewconfig/
    :alt: License

.. |versions| image:: https://pypip.in/py_versions/pyramid_notebook/badge.png
    :target: https://pypi.python.org/pypi/websauna.viewconfig/
    :alt: Supported Python versions

+-----------+-----------+
| |cov|     ||downloads||
+-----------+-----------+
| |ci|      | |license| |
+-----------+-----------+
| |versions|| |latest|  |
+-----------+-----------+

.. contents:: :local:

Features
--------

``websauna.viewconfig`` provides a class decorator ``@view_overrides`` which allows subclasses to partially override parent class view configuration. The primary use case is to have generic class views which you can subclass for more specific use cases. The pattern is very powerful when combined with Pyramid's travesing contexts.

Example:

* There is a generic edit view for all of your models called *GenericEdit*

* But for a specific model, let's say Car, you want to override parts of *GenericEdit* e.g. to include a widget to handle car colour selection. Other models, like House and Person, still use *GenericEdit*.

The code would be::

     from websauna.viewconfig import view_overrides

     # We define some model structure for which we are going to create edit views
     class BaseModel:
          pass


     class House(BaseModel):
          pass


     class Car(BaseModel):
          pass


     # This is the base edit view class. You can use it as is or subclass it to override parts of it.
     class GenericEdit:

         widgets = ["name", "price"]

         def __init__(self, context, request):
             self.context = context
             self.request = request

         @view_config(name="edit", context=BaseModel)
         def edit(self):
             # Lot's of edit logic code goes here which
             # we don't want to repeat....
             pass


     # This overrides edit() method from GenericEdit.edit() with a different @view_config(context) parameters. 
     # Otherwise @view_config() parameters are copied as is.
     @view_overrides(context=Car)
     class CarEdit(GenericEdit):
         widgets = ["name", "price", "color", "year]


      # Some dummy traversing which shows how view are mapped to traversing context
      class Root:
          """Pyramid's traversing root."""

          def __init__(self, request):
               pass

          def __getitem__(self, name):
              if is_car(name):
                    return Car(name)
               else:
                    return House(name):


Now one could traverse edit views like::

     /my_house/edit
     /my_car/edit

... and the latter would serve car-specific edit form.

The ``@view_overrides`` pattern can be also used with routing based views to override e.g ``route_name`` and ``renderer`` (the template of subclass view). For those examples, please see testing source code.

The implementation is based on `venusian.lift() <http://venusian.readthedocs.org/en/latest/api.html#venusian.lift>`_ function with the overriding bits added in.

Development and tests
---------------------

To run tests::

    pip install -e ".[test]"
    py.test websauna/viewconfig

To run coverage::

     py.test --cov websauna.viewconfig --cov-report xml

All the testing on drone.io::

    pip install -U pytest
    pip install -e ".[test]"
    py.test --cov websauna.viewconfig --cov-report xml
    codecov --token="xxx"

Author
------

Mikko Ohtamaa (`blog <https://opensourcehacker.com>`_, `Facebook <https://www.facebook.com/?q=#/pages/Open-Source-Hacker/181710458567630>`_, `Twitter <https://twitter.com/moo9000>`_)
