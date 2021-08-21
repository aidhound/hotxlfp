# hotxlfp changelog

## 0.0.15

* Fixed bugs in FLOOR function.
* Fixed bugs in ATAN2

## 0.0.14

* Fixed using a parser within a parser.

## 0.0.13

* Fixed comparison between floats and integers giving inverted results
* Fixed decimals without a leading zero resulting in an error.

## 0.0.12

* Fix a bug where formulas using criteria like COUNTIF would not match correctly if the criteria had characters like ',' or ')'

## 0.0.11

* Support for RAND, RANDBETWEEN, DAYS, ISNONTEXT and COT

## 0.0.10

* Support for FACT, FACTDOUBLE, ARABIC, ROMAN and TODAY
* Fixed bugs where the result was not an error when it should 

## 0.0.9

* Fixed bug with undefined variables not returning a #NAME? error

## 0.0.8

* Fix bug with accented charactes in criteria

## 0.0.7

* Fixed a bug with criteria evaluation in formulas such as COUNTIF

## 0.0.6

* bidimensional arrays are now supported in some cases
* INDEX is now supported
* TEXTJOIN is now supported
* SUBSTITUTE is now supported
* LEN is now supported

## 0.0.5

* DECIMAL is now supported
* BASE is now supported
* ISLOGICAL is now supported
* ISNUMBER is now supported
* DATEVALUE is now supported
* Much better implicit type conversion in operators

## 0.0.4

First version that actually works if you install using pip
