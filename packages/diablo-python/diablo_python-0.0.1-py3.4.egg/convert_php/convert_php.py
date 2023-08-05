"""
Module for converting and translating PHP data to other 
formats and structures. This includes the ability to unserialize
and translate arrays to other languages.
"""

__author__  = "Brad Busenius"
__copyright__ = "Copyright 2014"
__credits__ = ['Brad Busineus']
__version__ = "0.0.1"
__maintainer__ = "Brad Busenius"
__status__ = "Testing"

import phpserialize
from collections import OrderedDict
import pprint
import json

class ConvertPHP():
    """
    A class for unserializing and translating php data structures
    to other formats and languages.
    """
    def __init__(self):
        """
        Initialize the object.
        """
        self.data_structure = ''
        self.built_in = set(['python', 'json'])

    def __str__(self):
        """
        String representation of the class.
        """
        return self.data_structure

    def is_built_in(self, language):
        """
        Tests to see if a language is a built in type
        supported by python.
        
        Args:
            language: string, language to test for.

        Returns: 
            boolean
        """
        return language in self.built_in

    # Language specific values 
    lang_specific_values = {'php': { 
                                    'True'  : 'true',
                                    'False' : 'false',
                                    'None'  : 'null'},
                            'javascript' : {
                                    'True' : 'true',
                                    'False' : 'false',
                                    'None' : 'null'},
                            'ocaml' : {
                                    'True' : 'true',
                                    'False': 'false'}}

    # Language specific wrapper templates
    outer_templates = {'php' : 'array (\n%s\n);',
                       'javascript' : 'var jsObject = {\n%s\n}',
                       'ocaml' : 'let map = [|\n%s\n|] ;;'}

    def get_built_in(self, language, level, data):
        """
        Gets the return string for a language that's supported by python.
        Used in cases when python provides support for the conversion.
    
        Args:
            language: string the langage to return for.

            level: integer, the indentation level.

            data: python data structure being converted (list of tuples)

        Returns:
            None, updates self.data_structure  
        """
        # Language is python
        pp = pprint.PrettyPrinter(indent=level)

        lookup = {'python' : pp.pformat(data),
                  'json' : str(json.dumps(data, sort_keys=True, indent=level, separators=(',', ': ')))}

        self.data_structure = lookup[language]

    def get_inner_template(self, language, template_type, indentation, key, val):
        """
        Gets the requested template for the given language.

        Args:
            language: string, the language of the template to look for.

            template_type: string, 'iterable' or 'singular'. 
            An iterable template is needed when the value is an iterable
            and needs more unpacking, e.g. list, tuple. A singular template 
            is needed when unpacking is complete and the value is singular, 
            e.g. string, int, float.

            indentation: int, the indentation level.
    
            key: multiple types, the array key.

            val: multiple types, the array values

        Returns:
            string, template formatting for arrays by language.
        """
        #Language specific inner templates
        inner_templates = {'php' : {
                                'iterable' : '%s%s => array \n%s( \n%s%s),\n' % (indentation, key, indentation, val, indentation),
                                'singular' : '%s%s => %s, \n' % (indentation, key, val) },
                           'javascript' : {
                                'iterable' : '%s%s : {\n%s\n%s},\n' % (indentation, key, val, indentation),
                                'singular' : '%s%s: %s,\n' % (indentation, key, val)},
                           'ocaml' : { 
                                'iterable' : '%s[| (%s, (\n%s\n%s))|] ;;\n' % (indentation, key, val, indentation),
                                'singular' : '%s(%s, %s);\n' % (indentation, key, val)}}

        return inner_templates[language][template_type]

    def translate_val(self, language, value):
        """
        Translates string representations of language specific 
        values that vary between languages. Used to translate
        python values to their counterparts in other languages.

        Args:
            language: string, the language for which to
            return values.

            value: string, the value to translate.

        Returns:
            string representation of a value in a given language.
        """
        return self.lang_specific_values[language][value]


    def is_iterable(self, data):
        """
        Checks to see if an object is an iterable.

        Args:
            data: a data object.

        Returns:
            boolean
        """
        try:
            iterate = iter(data)
            return True
        except:
            return False 


    def translate_array(self, string, language, level=3, retdata=False):
        """Unserializes a serialized php array and prints it to
        the console as a data structure in the specified language.
        Used to translate or convert a php array into a data structure 
        in another language. Currently supports, PHP, Python, Javascript,
        and JSON. 

        Args:
            string: a string of serialized php
        
            language: a string representing the desired output 
            format for the array.

            level: integer, indentation level in spaces. 
            Defaults to 3.

            retdata: boolean, the method will return the string
            in addition to printing it if set to True. Defaults 
            to false.

        Returns:
            None but prints a string to the console if retdata is 
            False, otherwise returns a string.
            """
        language = language.lower()
        assert self.is_built_in(language) or language in self.outer_templates, \
            "Sorry, " + language + " is not a supported language."

        # Serialized data converted to a python data structure (list of tuples)
        data = phpserialize.loads(bytes(string, 'utf-8'), array_hook=list, decode_strings=True)

        # If language conversion is supported by python avoid recursion entirely
        # and use a built in library
        if self.is_built_in(language):
            self.get_built_in(language, level, data) 
            print(self)
            return self.data_structure if retdata else None

        # The language is not supported. Use recursion to build a data structure.
        def loop_print(iterable, level=3):
            """
            Loops over a python representation of a php array 
            (list of tuples) and constructs a representation in another language.
            Translates a php array into another structure.

            Args:
                iterable: list or tuple to unpack.

                level: integer, number of spaces to use for indentation
            """
            retval = ''
            indentation = ' ' * level

            # Base case - variable is not an iterable
            if not self.is_iterable(iterable) or isinstance(iterable, str):
                non_iterable = str(iterable)
                return str(non_iterable)
             
            # Recursive case
            for item in iterable:
                # If item is a tuple it should be a key, value pair
                if isinstance(item, tuple) and len(item) == 2:
                    # Get the key value pair
                    key = item[0]
                    val = loop_print(item[1], level=level+3)
            
                    # Translate special values
                    val = self.translate_val(language, val) if language in self.lang_specific_values \
                          and val in self.lang_specific_values[language] else val
     
                    # Convert keys to their properly formatted strings
                    # Integers are not quoted as array keys
                    key = str(key) if isinstance(key, int) else '\'' + str(key) + '\''

                    # The first item is a key and the second item is an iterable, boolean
                    needs_unpacking = hasattr(item[0],'__iter__') == False \
                                      and hasattr(item[1],'__iter__') == True 

                    # The second item is an iterable
                    if needs_unpacking:
                        retval += self.get_inner_template(language, 'iterable', indentation, key, val)
                    # The second item is not an iterable
                    else:
                        # Convert values to their properly formatted strings
                        # Integers and booleans are not quoted as array values
                        val = str(val) if val.isdigit() or val in self.lang_specific_values[language].values() else '\'' + str(val) + '\''

                        retval += self.get_inner_template(language, 'singular', indentation, key, val) 

            return retval
    
        # Execute the recursive call in language specific wrapper template
        self.data_structure = self.outer_templates[language] % (loop_print(data))
        print(self)
        return self.data_structure if retdata else None

