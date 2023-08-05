## benchit - Quick n' Dirty Python Benchmarkin'

Quickly find where your code is spending its time.

[![Build Status](https://secure.travis-ci.org/scuml/benchit.png?branch=master)](http://travis-ci.org/scuml/benchit)
[![Downloads](https://img.shields.io/pypi/dw/bench-it.svg)](https://pypi.python.org/pypi/bench-it)

### Example

    >>> from benchit import BenchIt
    >>> b = BenchIt() # starts the timer
    >>> # do stuff
    >>> b.mark("Stuff Done")
    >>> for i in range(1,5):
    ...   b.mark("In loop")
    ...   pass  # more stuff done
    >>> b.mark("More stuff completed")
    >>> b.display()
    +----------------------+----------+------+-------+----------+---------+---------+
    | Marker               | Method   | Line | Loops | Avg Time | Runtime | Percent |
    +----------------------+----------+------+-------+----------+---------+---------+
    | Stuff Done           | <module> |    2 |     1 |  0.59003 | 0.59003 |    5.86 |
    | In loop              | <module> |    2 |     4 |  1.37800 | 5.51199 |   54.78 |
    | More stuff completed | <module> |    6 |     1 |  3.60235 | 3.60235 |   35.80 |
    | _display             | <module> |   53 |     1 |  0.35842 | 0.35842 |    3.56 |
    +----------------------+----------+------+-------+----------+---------+---------+
    Total runtime: 10.06

### How to Use

Instantiating the class starts the timer.

    b = BenchIt()


### Methods

`__init__()` Instantiate and start the timer.

`benchit.mark(marker_name)` Add marker at this point.

`benchit.stop()` Stop the timer.

`benchit.display(marker_name)` Display the table.  Stops the timer if running.


###### Credits
*Special thanks Luke Maurits for [prettytable](https://pypi.python.org/pypi/PrettyTable)*