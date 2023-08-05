"""
This module has very basic math functions not found in the math module.
Some of the functions here, require the math module.
"""

__author__ = "Brad Busenius"
__copyright__ = "Copyright 2014"
__credits__ = ['Brad Busineus']
__version__ = "0.0.1"
__maintainer__ = "Brad Busenius"
__status__ = "Testing"

import math, warnings
from decimal import *

def miles_to_feet(miles):
    """
    Converts a number of miles to feet.

    Args:
        miles: Number of miles we want to convert.

    Returns:
        Floating point number as the number of
        feet in the given miles.
    """

    return miles * float(5280)


def total_seconds(hours, minutes, seconds):
    """
    Returns the number of seconds in the given number of hours, 
    minutes, and seconds.

    Args:
        hours:
            Integer, number of hours.

        minutes:
            Integer, number of minutes.

        seconds:
            Integer, number of seconds.

    Returns:
        Integer, time in seconds.
    """

    return (hours * 60 + minutes) * 60 + seconds


def rectangle_perimeter(width, height):
    """
    Returns the perimeter of a rectangle with the given width and height.

    Args:
        width:
            Integer or float, width of the rectangle.

        height:
            Integer or float, height of the rectangle.

    Returns:
        Integer or float, perimeter of a rectangle.
    """

    return width * 2 + height * 2


def rectangle_area(width, height):
    """Returns the area of a rectangle with the given width and height.
    
    Args:
        width:
            Integer or float, width of the rectangle.

        height: Integer or float, height of the rectangle.

    Returns:
        The area of a rectangle as an integer or float.
    """

    return width * height


def circle_circumference(radius):
    """
    Returns the circumference of a circle.

    Args:
        radius: The radius of a circle.

    Returns: 
        Integer > circumference of a circle.

    Requires:
        The math module.
    """
    return radius * 2 * math.pi


def circle_area(radius):
    """
    Returns the area of a circle.

    Args:
        radius: The radius of a circle.

    Returns:
        The area of a circle as an integer.

    Requires:
        The math module.
    """
    return math.pi * radius ** 2


def compound_interest(principal, annual_rate, years):
    """
    Returns the future value of money invested at an annual
    interest rate, compounded annually for a given number of years.

    Args:
        principal: The beginning ammount of money invested

        annual_rate: The interest rate paid out

        years: The number of years invested

    Returns:
        A basic calculation of compound interest.
    """
    
    return principal * (1 + 0.01 * annual_rate) ** years


def future_value(present_value, annual_rate, periods_per_year, years):
    """
    Calculates the future value of money invested at an anual interest rate,
    x times per year, for a given number of years.

    Args:
        present_value: int or float, the current value of the money (principal). 
        
        annual_rate: float 0 to 1 e.g., .5 = 50%), the interest rate paid out.
        
        periods_per_year: int, the number of times money is invested per year.

        years: int, the number of years invested.

    Returns:
        Float, the future value of the money invested with compound interest.
    """

    # The nominal interest rate per period (rate) is how much interest you earn during a 
    # particular length of time, before accounting for compounding. This is typically 
    # expressed as a percentage.
    rate_per_period = annual_rate / float(periods_per_year)

    # How many periods in the future the calculation is for.
    periods = periods_per_year * years
    
    return present_value * (1 + rate_per_period) ** periods


def point_distance(point1, point2):
    """
    Computes the distance beteen two points on a plane.

    Args:
        point1: Tuple or list, the x and y coordinate of the first point.

        point2: Tuple or list, the x and y coordinate of the second point.
        
    Returns:
        The distance between the two points as a floating point number.
    """
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


def triangle_area(point1, point2, point3):
    """
    Uses Heron's formula to find the area of a triangle 
    based on the coordinates of three points.

    Args:
        point1: list or tuple, the x y coordinate of point one.

        point2: list or tuple, the x y coordinate of point two.

        point3: list or tuple, the x y coordinate of point three.

    Returns:
        The area of a triangle as a floating point number.

    Requires:
        The math module, point_distance().
    """

    """Lengths of the three sides of the triangle"""
    a = point_distance(point1, point2)
    b = point_distance(point1, point3)
    c = point_distance(point2, point3)
    
    """Where s is the semiperimeter"""
    s = (a + b + c) / 2.0
    
    """Return the area of the triangle (using Heron's formula)"""
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


def is_leap_year(year):
    """
    Checks to see if a given year is a leap year.

    Args:
        Integer, the year to test.

    Returns: 
        Boolean
    """
    if (year % 400) == 0:
        return True
    elif (year % 100) == 0:
        return False
    elif (year % 4) == 0:
        return True
    else:
        return False


def regular_polygon_area(number_of_sides, length_of_sides):
    """
    Calculates the area of a regular polygon (with sides of equal length).

    Args:
        number_of_sides: Integer, the number of sides of the polygon

        length_of_sides: Integer or floating point number, the length of the sides

    Returns:
        The area of a regular polygon as an integer or floating point number

    Requires:
        The math module
    """
    return (0.25 * number_of_sides * length_of_sides ** 2) / math.tan(math.pi/number_of_sides)


def median(data):
    """
    Calculates  the median of a list of integers or floating point numbers.

    Args:
        data: A list of integers or floating point numbers

    Returns:
        Sorts the list numerically and returns the middle number if the list has an odd number 
        of items. If the list contains an even number of items the mean of the two middle numbers
        is returned.    
    """
    ordered = sorted(data)
    length = len(ordered)
    if length % 2 == 0:
         return (ordered[math.floor(length / 2) - 1] + ordered[math.floor(length / 2)]) / 2.0
                
    elif length % 2 != 0:
        return ordered[math.floor(length / 2)]


def average(numbers, numtype='float'):
    """
    Calculates the average or mean of a list of numbers

    Args:
        numbers: a list of integers or floating point numbers.

        numtype: string, 'decimal' or 'float'; the type of number to return.

    Returns:
        The average (mean) of the numbers as a floating point number
        or a Decimal object. 

    Requires:
        The math module
    """
    if type == 'decimal':
        return Decimal(sum(numbers)) / len(numbers)
    else:
        return float(sum(numbers)) / len(numbers)


def variance(numbers, type='population'):
    """
    Calculates the population or sample variance of a list of numbers. 
    A large number means the results are all over the place, while a 
    small number means the results are comparatively close to the average.

    Args:
        numbers: a list  of integers or floating point numbers to compare.

        type: string, 'population' or 'sample', the kind of variance to be computed.

    Returns:
        The computed population or sample variance. 
        Defaults to population variance.

    Requires:
        The math module, average()
    """
    mean = average(numbers)
    variance = 0
    for number in numbers:
        variance += (mean - number) ** 2        
    
    if type == 'population':
        return variance / len(numbers)
    else:
        return variance / (len(numbers) - 1)

def standard_deviation(variance):
    """
    Calculates the standard deviation.

    Args:
        variance: The variance of a group of numbers.

    Returns:
        The standard deviation as a floating point number.
    """
    return variance ** 0.5

def get_percentage(a, b, i=False, r=False):
    """
    Finds the percentage of one number over another. 

    Args:
        a: The number that is a percent, int or float.

        b: The base number that a is a percent of, int or float.

        i: Optional boolean integer. True if the user wants the result returned as 
        a whole number. Assumes False.

        r: Optional boolean round. True if the user wants the result rounded. 
        Rounds to the second decimal point on floating point numbers. Assumes False.

    Returns:
        The argument a as a percentage of b. Throws a warning if integer is set to True
        and round is set to False.
    """
    # Round to the second decimal 
    if i == False and r == True:
        percentage =  round(100.0 * (float(a) / b), 2)
        
    # Round to the nearest whole number
    elif (i == True and r == True) or (i == True and r == False):
        percentage =  int(round(100 * (float(a) / b)))
    
        # A rounded number and an integer were requested
        if r == False:
            warnings.warn("If integer is set to True and Round is set to False, you will still get a rounded number if you pass floating point numbers as arguments.")
        
    # A precise unrounded decimal
    else:
        percentage =  100.0 * (float(a) / b)
        
    return percentage

def get_slope(point1, point2):
    """
    Calculate the slope of the line connecting two points on a grid.

    Args:
        point1: Tuple or list, the x and y coordinate of the first point.

        point2: Tuple or list, the x and y coordinate of the second point

    Returns:
        the slope of a line connecting two points on a grid.
    """
    return (float(point2[1]) - point1[1]) / (float(point2[0]) - point1[0])

def get_full_binary_tree_leaves(height):
    """
    Calculate the number of leaves in a complete binary tree in which each internal 
    node has exactly two children. A full binary tree is complete if every leaf 
    in the tree has the same depth. A leaf is a node without children

    Args:
        height: integer, the height of the tree. Height is defined by the number
        of edges from the furthest child to the root. An edge is the line segment
        that runs between and connects nodes.
    """
    return 2**height

def get_full_binary_tree_nodes(height):
    """
    Calculate the number of internal nodes in a complete binary tree in which each 
    internal node has exactly two children. A full binary tree is complete if every 
    leaf in the tree has the same depth. Internal nodes include both leaves and 
    internal nodes. The root node is also included in this calculation.

    Args:
        height: integer, the height of the tree. Height is defined by the number
        of edges from the furthest child to the root. An edge is the line segment
        that runs between and connects nodes.
    """
    return 2**(height + 1) - 1 

def take_home_pay(gross_pay, employer_match, taxes_and_fees, numtype='float'):
    """
    Calculate net take-home pay including employer retirement savings match 
    using the formula laid out by Mr. Money Mustache: 
    http://www.mrmoneymustache.com/2015/01/26/calculating-net-worth/

    Args:
        gross_pay: float or int, gross monthly pay.

        employer_match: float or int, the 401(k) match from your employer.
    
        taxes_and_fees: list, taxes and fees that are deducted from your paycheck.

        numtype: string, 'decimal' or 'float'; the type of number to return.

    Returns:
        your monthly take-home pay. 
    """
    if numtype == 'decimal':
        return (Decimal(gross_pay) + Decimal(employer_match)) - Decimal(sum(taxes_and_fees))
    else:
        return (float(gross_pay) + float(employer_match)) - sum(taxes_and_fees)

def savings_rate(take_home_pay, spending, numtype='float'):
    """Calculate net take-home pay including employer retirement savings match 
    using the formula laid out by Mr. Money Mustache: 
    http://www.mrmoneymustache.com/2015/01/26/calculating-net-worth/

    Args:
        take_home_pay: float or int, monthly take-home pay

        spending: float or int, monthly spending

        numtype: string, 'decimal' or 'float'; the type of number to return.

    Returns:
        your monthly savings rate expressed as a percentage.
    """

    if numtype == 'decimal': 
         return ((Decimal(take_home_pay) - Decimal(spending)) / (Decimal(take_home_pay))) * Decimal(100.0)
    else:
        return ((float(take_home_pay) - float(spending)) / (float(take_home_pay))) * 100.0


