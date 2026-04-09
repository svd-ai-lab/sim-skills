# Introduction to Python

## The Python Programming Language

Python is a general purpose, object-oriented, interpreted high-level programming language. It is known as a clear and highly readable language with a large and comprehensive standard library. Python can be utilized for both object-oriented and functional programming. It implements dynamic typing system and automatic memory management.

## Python version

The Python version that is used by ANSA is Python v3.11.9.

## Data Types

The term “Data Type” determines the different kind of data that a variable or a function can hold. The Data Types consist of the common used types
like integer or floating point numbers, strings, matrices etc, which are built-in the python infrastructure, as well as user defined types.
The following paragraphs describe the Python built-in data types.

**Integer**

The integer data type is used by variables that can only have whole numbers as values, either positive, negative or zero.

```python
my_var = 10
```

**Floating Point**

Values that are not integral are stored as floating point numbers. A floating point variable can be
expressed as a decimal number such as 112.5, or with an exponent such as 1.125E2. In the latter case
the decimal part is multiplied by the power of 10 after the E symbol.
A floating point must contain a decimal point, or an exponent or both.

```python
my_var = 112.5
```

**Complex**

Complex numbers have a real and an imaginary part, both of them being represented as a floating point number.

```python
c = 4+3j
```

**Boolean**

A boolean data type can represent two discrete logical states, thus being able to have only two values: ‘True’ and ‘False’

```python
b = True
```

**String**

A string, is declared as a series of printable text characters representing human readable stuff. A string
value is enclosed in quotes (e.g. “this is a string”) and can be assigned to any variable for storage and
easy access. String variables are represented as lists of characters.

```python
s = 'a string'
s = "a string"
```

**List**

A List is an ordered collection object type. A list can contain any type of an object such as integer, float
string, other lists, custom objects etc. Lists are mutable objects. Objects can be added, removed and
their order can be changed. The List object is similar to the matrix of the ANSA Scripting language.

```python
my_list = [1, 2.3, 'world', [2, 3.7, 8.5]]
my_list.append('python')
print('result:', my_list[2])
```

**Tuple**

A tuple is an ordered sequence of Python objects, just like a List. In contrast to lists, tuples are immutable objects,
meaning that they cannot be modified. Defining a tuple is as simple as putting different comma-separated values
between parenthesis.

```python
tup1 = (1, 2, 3)
tup2 = ('one', 'two', 'three')
print(tup1 + tup2)
```

**Dictionary**

A Dictionary is an unordered collection. In a dictionary, items are stored and fetched by a key instead of a
positional offset. Indexing a dictionary is a very fast and powerful operation. Dictionaries are the
equivalent to Maps of the ANSA Scripting Language.

```python
my_dict = {'planet':'earth', 'world':3, 'test':10}
print('result:', my_dict['world'])
my_dict = {'planet':'earth', 'world':3, 'nest':{'test':10, 'entity':10}}
print('result:', my_dict['nest']['entity'])
```

**The del Statement**

The del statement is used to delete references to objects.

```python
del data[k]
del data[i:j]
del obj.attr
del variable
```

**The None Object**

Python provides a special object called None, which is always considered to be false. It is a special data
type and it serves as an empty placeholder.

## if statements and branching

### The “if-else” blocks and the logical operators

The if statement is the basic decision statement of an algorithm. Its operation is based on the evaluation of a
condition that will yield a result that is either true or false. If the condition is true (i.e. not equal to 0),
then the if-block of statements is executed. If the condition is false, then the else-block of statements is
executed. The if statement general form is:

```python
if condition:
    statement
```

The alternative line of execution is created with elif and else:

```python
if condition:
    statement
elif condition:
    statement
else:
    statement
```

Since the condition is interpreted as a logical operator, the operators used for its expression are the
logical relational operators. Such operators are summarized in the table below:

| 

operator | 

meaning | 

|---|---|

| 

 | 

greater than | 

| 

>= | 

greater than or equal to | 

| 

== | 

equal to | 

| 

!= | 

not equal to | 

| 

or | 

Logical OR | 

| 

and | 

Logical AND | 

| 

not | 

Logical NOT | 

It is also possible for an object to be the condition itself.

```python
if x:
    statement
```

In this case Python implicitly converts x to boolean, based on some specific rules, and checks if the value
is True or False, in order to execute the statement.

## Loop statements

A loop comprises of a block of statements that are executed repetitively. When the end of the loop is
reached, the block is repeated from the start of the loop. Python provides two loop types; the for loop
and the while loop.

### The for loop statement

The for statement allows the iteration over the elements of a sequence. For loops do not maintain any
explicit counter. The general form of the statement is:

```python
for  in :
    do something to 
```

An example of the statement use is given below:

```python
 all_properties = ["PSHELL", "PCOMP", "PBAR", "PBEAM", "PELAS"]

 for property in all_properties:
     print(property)

# The result is:
# PSHELL
# PCOMP
# PBAR
# PBEAM
# PELAS
```

In order to iterate over the list, while having the index available, the function range() can be used.
Its general form is: range([start], stop[, step]), where start and stop is the initial and the ending value of the
sequence respectively, and step is the increment or decrement value between the consecutive numbers.

An example of using the function range() to iterate over specific items of a list can be seen below:

```python
 all_properties = ["PSHELL", "PCOMP", "PBAR", "PBEAM", "PELAS"]
 length = len(all_properties)

 for i in range(0, length, 2):
     property = all_properties[i]
     print(property)

# The result is:
# PSHELL
# PBAR
# PELAS
```

### The while loop statement

The while statement introduces a conditional exit loop. The program executes the specified statements
repetitively for as long as the given condition remains true (i.e. not equal to 0). Its general form is:

```python
while condition:
    body-statement
```

If operators are to be used for the expression of the condition, these must be of logical relational type.

```python
 a = 0
 while a **Note:** 

Note

Please refer to the official Python 3 documentation for more information on module management.

### Importing modules using the ImportCode Function

The ANSA API function “ansa.ImportCode(filepath)”, allows to easily import Python modules.
It imports both compiled and ASCII modules.

An example can be seen below:

```python
import ansa
ansa.ImportCode('/home/demo/Desktop/my_library.pyb')

def main():
    myLibrary.myFunction()
```