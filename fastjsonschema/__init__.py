"""
This project was made to come up with fast JSON validations. Just let's see some numbers first:

 * Probalby most popular ``jsonschema`` can take in tests up to 7 seconds for valid inputs
   and 1.6 seconds for invalid inputs.
 * Secondly most popular ``json-spec`` is even worse with up to 11 and 2.6 seconds.
 * Lastly ``validictory`` is much better with 640 or 30 miliseconds, but it does not
   follow all standards and it can be still slow for some purposes.

That's why this project exists. It compiles definition into Python most stupid code
which people would had hard time to write by themselfs because of not-written-rule DRY
(don't repeat yourself). When you compile definition, then times are 90 miliseconds for
valid inputs and 5 miliseconds for invalid inputs. Pretty amazing, right? :-)

You can try it for yourself with included script:

.. code-block:: bash

    $ make performance
    fast_compiled        valid      ==> 0.09240092901140451
    fast_compiled        invalid    ==> 0.004246290685236454
    fast_not_compiled    valid      ==> 6.710726021323353
    fast_not_compiled    invalid    ==> 1.5449269418604672
    jsonschema           valid      ==> 6.963333621155471
    jsonschema           invalid    ==> 1.6309524956159294
    jsonspec             valid      ==> 10.576010060030967
    jsonspec             invalid    ==> 2.6199211929924786
    validictory          valid      ==> 0.6349993739277124
    validictory          invalid    ==> 0.03125431900843978

This library follows and implements `JSON schema v4 <http://json-schema.org>`_. Sometimes
it's not perfectly clear so I recommend also check out this `understaning json schema
<https://spacetelescope.github.io/understanding-json-schema>`_.

Note that there are some differences compared to JSON schema standard:

 * Regular expressions are full Python ones, not only what JSON schema allows. It's easier
   to allow everything and also it's faster to compile without limits. So keep in mind that when
   you will use more advanced regular expression, it may not work with other library.
 * JSON schema says you can use keyword ``default`` for providing default values. This implementation
   uses that and always returns transformed input data.

Support only for Python 3.3 and higher.
"""

from os.path import exists

from .exceptions import JsonSchemaException
from .generator import CodeGenerator
from .ref_resolver import RefResolver

__all__ = ('JsonSchemaException', 'compile', 'write_code')


def compile(definition, handlers={}):
    """
    Generates validation function for validating JSON schema by ``definition``. Example:

    .. code-block:: python

        import fastjsonschema

        validate = fastjsonschema.compile({'type': 'string'})
        validate('hello')

    This implementation support keyword ``default``:

    .. code-block:: python

        validate = fastjsonschema.compile({
            'type': 'object',
            'properties': {
                'a': {'type': 'number', 'default': 42},
            },
        })

        data = validate({})
        assert data == {'a': 42}

    Exception :any:`JsonSchemaException` is thrown when validation fails.
    """
    resolver = RefResolver.from_schema(definition, handlers=handlers)
    # get main function name
    name = resolver.get_scope_name()
    code_generator = CodeGenerator(definition, resolver=resolver)
    # Do not pass local state so it can recursively call itself.
    global_state = code_generator.global_state
    exec(code_generator.func_code, global_state)
    return global_state[name]

def write_code(filename, definition, handlers={}, overwrite=False):
    """
    Generates validation function for validating JSON schema by ``definition``
    and write it to file.
    
    Arguments:
        filename (str): Filename where generated code is written
        definition (dict): JSON Schema defining validation rules
        handlers (dict): A mapping from URI schemes to functions
        that should be used to retrieve them.
        overwrite (bool): Set to `True` to overwrite existing file

    Returns:
        validation function name (str)

    Raises:
        JsonSchemaException: is thrown when generation fails.
    

    Create validator Example:

    .. code-block:: python

        import fastjsonschema

        schema = {'type': 'string'}
        name = fastjsonschema.write_code('validator.py', schema)
        print(name)

    Generated file usage Example:

    .. code-block:: python

        from validator import validate

        validate('example')

    Exception :any:`JsonSchemaException` is thrown when validation fails.
    """

    if exists(filename) and overwrite == False:
        raise JsonSchemaException('file {} already exists'.format(filename))
    resolver = RefResolver.from_schema(definition, handlers=handlers)
    # get main function name
    name = resolver.get_scope_name()
    code_generator = CodeGenerator(definition, resolver=resolver)
    # Do not pass local state so it can recursively call itself.
    global_state_code = code_generator.global_state_code
    with open(filename, 'w', encoding='UTF-8') as out:
        print(global_state_code, file=out)
        print(code_generator.func_code, file=out)
    return name
