# hotxlfp changelog

## 1.1.0

**Compatibility:** array literals now return lists of rows. For example, `{1,2}`
returns `[[1, 2]]` and `{1;2}` returns `[[1], [2]]`, rather than flat lists.
Applications that consume literal results directly may need to adjust. Arrays
supplied through callbacks retain their original shapes.

* Preserve array-literal orientation: commas or backslashes separate columns, semicolons separate rows, and omitted entries are `None`. Arrays must be rectangular.
* Broadcast array arithmetic across rows, columns and scalars, preserving row alignment and returning `#N/A` for unmatched cells.
* Keep typed Excel errors available to enclosing functions such as `IFERROR` and `IFNA`. Fix error propagation in logical, comparison, concatenation, text, lookup and numeric functions. `IFERROR` and `IFNA` also handle nested arrays while preserving their shapes.
* Make function names and custom function registration case-insensitive. Unknown functions and variables produce handleable `#NAME?` errors. Callback setters can explicitly override results with `None`.
* Update `COUNT` to recognize numeric and date strings directly and inside arrays and references. Array booleans, blanks, unrecognized text and typed errors are excluded; direct booleans and native dates still count. Counting numeric and date strings in arrays is an intentional difference from Excel.
* Align `ISBLANK` with the existing blank policy in `COUNTA` and `COUNTBLANK`: both `None` and `""` are blank. Document the intentional differences from Excel in the README.
* Add `ROWS`, and support both row and column vectors in `MATCH` and `INDEX`. `MATCH` skips error cells while preserving their positions in the vector.
* Support nested matching range shapes in `SUMIFS`, `AVERAGEIFS` and `MAXIFS`, preserving selected aggregate errors. Return `#DIV/0!` when `AVERAGEIFS` has no matches, and handle negative maxima in `MAXIFS` correctly.
* Preserve typed errors supplied as criterion arguments in `SUMIF`, `COUNTIF`, `AVERAGEIF`, `SUMIFS`, `AVERAGEIFS` and `MAXIFS`, so enclosing error handlers can catch them.
* Return `#DIV/0!` for empty `AVERAGE` and `AVERAGEA` calculations, and preserve errors through `AVEDEV`. Validate `LARGE` ranks against the flattened numeric values. Return empty text for zero-length `RIGHT` and `RIGHTB` calls.
* Return `#NUM!` for nonfinite numeric inputs, conversions and arithmetic overflow, while retaining support for arbitrarily large integers.

## 1.0.3

* Plain `datetime.date` objects (not just `datetime.datetime`) are now accepted everywhere a date can be used: the date functions (`DATE`, `DAYS`, `EDATE`, `YEAR`, `MONTH`, `DAY`, ...), `N`, and directly in arithmetic (`+`, `-`, `*`, `/`) and comparison operators, matching `datetime.datetime` behavior exactly.
* Include the generated PLY parser table in the package to avoid runtime write warnings in read-only installs.

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
