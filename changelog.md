# hotxlfp changelog

## 1.0.2

* Support for LARGE
* Fixes CONCATENATE was not working with numbers

## 1.0.1

* Support for TIME, TIMEVALUE (Thanks João Grazina)
* Support for WEEKDAY
* Support for TRIM

## 1.0.0

*DROPPED PYTHON 2 SUPPORT* hence the bump to 1.0.0 which reflects the breaking change and the project growing maturity.

* Support for LEFT, RIGHT, MID (Thanks João Grazina)
* Partial support for TEXT (Thanks Rodrigo Patrão)

## 0.0.16

* Fixed SWITCH formula returning N/A when the default value was "falsy" (like 0)

This release also brings a bunch of new supported formulas (Thanks Rodrigo Patrão)

* Support for SIGN function
* Support for SLOPE function
* Support for MAXIFS function
* Support for AVERAGEIFS
* Support for SUMIFS function
* Support for INT function
* Support for EDATE fuction
* Support for DATEDIF
* Support for NOW function
* Support for T, IMAGINARY and IMREAL

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
