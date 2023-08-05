import urllib.request, urllib.error, urllib.parse
import re

def get_web_file(path):
    """Gets a file over http.
    
    Args:
        path: string url of the desired file.

    Returns:
        The desired file as a string.        
    """
    response = urllib.request.urlopen(path)
    return response.read()

def copy_web_file_to_local(file_path, target_path):
    """Copies a file from its location on the web to a designated 
    place on the local machine.

    Args:
        file_path: Complete url of the file to copy, string (e.g. http://fool.com/input.css).

        target_path: Path and name of file on the local machine, string. (e.g. /directory/output.css)

    Returns:
        None.

    """
    response = urllib.request.urlopen(file_path)
    f = open(target_path, 'w')
    f.write(response.read()) 
    f.close()

def get_line_count(fname):
    """Counts the number of lines in a file.

    Args:
        fname: string, name of the file.

    Returns:
        integer, the number of lines in the file.

    """
    i = 0
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def indent_css(f, output):
    """Indentes css that has not been indented and saves it to a new file.
    A new file is created if the output destination does not already exist.

    Args:
        f: string, path to file.

        output: string, path/name of the output file (e.g. /directory/output.css).
    print type(response.read())

    Returns:
        None.
    """
    line_count = get_line_count(f)
    f = open(f, 'r+')
    output = open(output, 'r+')
    for line in range(line_count):
        string = f.readline().rstrip()
        if len(string) > 0:
            if string[-1] == ";":
                output.write("    " + string + "\n")
            else:
                output.write(string + "\n")
    output.close()
    f.close()

def add_newlines(f, output, char):
    """Adds line breaks after every occurance of a given character in a file.

    Args:
        f: string, path to input file.

        output: string, path to output file.

    Returns:
        None.
    """
    line_count = get_line_count(f)
    f = open(f, 'r+')
    output = open(output, 'r+')
    for line in range(line_count):
        string = f.readline()
        string = re.sub(char, char + '\n', string)
        output.write(string) 

def add_whitespace_before(char, input_file, output_file):
    """Adds a space before a character if there's isn't one already.
    
    Args:
        char: string, character that needs a space before it.

        input_file: string, path to file to parse.

        output_file: string, path to destination file.
    
    Returns:
        None.
    """
    line_count = get_line_count(input_file)
    input_file = open(input_file, 'r')
    output_file = open(output_file, 'r+')
    for line in range(line_count):
        string = input_file.readline()
        # If there's not already a space before the character, add one
        if re.search(r'[a-zA-Z0-9]' + char, string) != None:
            string = re.sub(char, ' ' + char, string)
        output_file.write(string)
    input_file.close()

def reformat_css(input_file, output_file):
    """Reformats poorly written css. This function does not validate or fix errors in the code.
    It only gives code the proper indentation. 

    Args:
        input_file: string, path to the input file.

        output_file: string, path to where the reformatted css should be saved. If the target file
        doesn't exist, a new file is created.

    Returns:
        None.
    """
    # Number of lines in the file.
    line_count = get_line_count(input_file)

    # Open source and target files.
    f = open(input_file, 'r+')
    output = open(output_file, 'w')

    # Loop over every line in the file.
    for line in range(line_count):
        # Eliminate whitespace at the beginning and end of lines.
        string = f.readline().strip()
        # New lines after { 
        string = re.sub('\{', '{\n', string)
        # New lines after ; 
        string = re.sub('; ', ';', string)
        string = re.sub(';', ';\n', string)
        # Eliminate whitespace before comments
        string = re.sub('} /*', '}/*', string)
        # New lines after } 
        string = re.sub('\}', '}\n', string)
        # New lines at the end of comments
        string = re.sub('\*/', '*/\n', string)
        # Write to the output file.
        output.write(string)

    # Close the files.
    output.close()
    f.close()

    # Indent the css.
    indent_css(output_file, output_file)

    # Make sure there's a space before every {
    add_whitespace_before("{", output_file, output_file)


def is_numeric(string):
    """
    Checks if a string is numeric. If the string value is an integer
    or a float, return True, otherwise False. Can be used to test 
    soley for floats as well. 
    
    Args:
        string: a string to test.

    Returns: 
        boolean
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def are_numeric(string_list):
    """
    Checks a list of strings to see that all values in the list are
    numeric. Returns the name of the offending string if it is  
    not numeric.

    Args:
        string_list: a list of strings to test.

    Returns:
        boolean or string
    """
    for string in string_list:
        if not is_numeric(string):
            return string
    return True


def is_int(string):
    """
    Checks if a string is an integer. If the string value is an integer
    return True, otherwise return False. 
    
    Args:
        string: a string to test.

    Returns: 
        boolean
    """
    try:
        a = float(string)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def total_hours(input_files):
    """
    Totals the hours for a given projct. Takes a list of input files for 
    which to total the hours. Each input file represents a project.
    There are only multiple files for the same project when the duration 
    was more than a year. A typical entry in an input file might look 
    like this: 

    8/24/14
    9:30-12:00 wrote foobar code for x, wrote a unit test for foobar code, tested. 
    2.5 hours
   
    Args:
        input_files: a list of files to parse.

    Returns:
        float: the total number of hours spent on the project.
    """
    hours = 0 
    # Look for singular and plural forms of the word
    # and allow typos.
    allow = set(['hours', 'hour', 'huors', 'huor'])
    for input_file in input_files:
        doc = open(input_file, 'r')
        for line in doc:
            line = line.rstrip()
            data = line.split(' ')
            if (len(data) == 2) and (is_numeric(data[0])) and (data[1].lower() in allow):
                hours += float(data[0])
        doc.close()
    return hours
