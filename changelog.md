# hotxlfp changelog

## 1.1.0

**Compatibility:** array literals now return lists of rows. For example, `{1,2}`
returns `[[1, 2]]` and `{1;2}` returns `[[1], [2]]`, rather than flat lists.
Applications that consume literal results directly may need to adjust. Arrays
supplied through callbacks retain their original shapes.

* Support rectangular array literals with omitted cells and scalar expressions/function calls. Broadcast array arithmetic across rows, columns and scalars, returning `#N/A` for unmatched cells.
* Preserve calculation errors, including `#SPILL!`, `#FIELD!` and `#CALC!`, for enclosing handlers. `IFERROR` and `IFNA` handle nested arrays and broadcast fallbacks. Correct math domains/overflow, rounding and numeral conversions; `^` accepts expressions and shares POWER's behavior.
* Make function calls and custom registration case-insensitive. Unknown names return catchable `#NAME?` errors, and callbacks can explicitly return `None`.
* Update `COUNT` to recognize numeric/date strings and exclude blanks, nonnumeric text, errors and array booleans. Align `ISBLANK` with the existing `None`/empty-string blank policy. Intentional Excel differences are documented in the [README](README.md).
* Add `ROWS`, `TOCOL`, `TOROW` and `UNIQUE`. Support row/column vectors in `MATCH` and `INDEX`; exact MATCH lookups normalize numeric text and preserve original positions.
* Correct numeric-text, logical and error criteria matching. Compile wildcard patterns once, with case-insensitive matching, Excel tilde escapes and literal brackets/path separators.
* Extend numeric-text coercion in aggregates; fix empty `MAX`/`MIN` results, conditional aggregation, selected-error handling, range/argument validation, statistical calculations and decimal ranks in `LARGE`. Separate `AVERAGEIF` arrays must have matching rectangular shapes.
* Standardize blank, boolean and numeric text conversion across text functions and `&`. Fix slicing arguments, `SUBSTITUTE` deletion and concatenation precedence; add value-preserving unary plus.
* Correct 1900 date serialization, fractional times, zero/time identity, `EDATE` month shifts and time truncation in `DATEVALUE`/`DAYS`. Preserve date results for day shifts and numeric results for date differences.

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
