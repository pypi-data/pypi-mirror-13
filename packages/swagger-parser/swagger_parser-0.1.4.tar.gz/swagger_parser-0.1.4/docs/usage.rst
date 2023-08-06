=====
Usage
=====

To use Swagger Parser in a project:

.. code:: python

  from swagger_parser import SwaggerParser

  parser = SwaggerParser(swagger_path='swagger_path')  # Init with file
  parser = SwaggerParser(swagger_dict={})  # Init with dictionary

  # Get an example of dict for the definition Foo
  parser.definitions_example.get('Foo')

  # Get the definition of a dictionary
  test = {
    'foo': 'bar'
  }
  parser.get_dict_definition(test)

  # Validate the definition of a dict
  parser.validate_definition('Foo', test)

  # Validate that the given data match a path specification
  parser.validate_request('/foo', 'post', body=test, query={'foo': 'bar'})

  # Get the possible return value of a path
  # It will return a dictionary with keys as status_code
  # and value as example of return value.
  parser.get_request_data('/foo', 'post', body=test)

  # Get an example of a correct body for a path
  parser.get_send_request_correct_body('/foo', 'post')
