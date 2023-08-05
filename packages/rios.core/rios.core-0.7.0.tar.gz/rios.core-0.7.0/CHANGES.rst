************************
RIOS.CORE Change History
************************


0.7.0 (2015-12-28)
==================

* Added support for the ``identifiable`` flag on Calculations.
* Added support for the ``meta`` property in Instruments, Calculation Sets,
  Forms, and Interactions.
* Enhanced validation of metadata values that are supposed to follow the HTTP
  Product Token format.
* Display duplicate IDs and more information in error messages.
* The ``get_full_type_definition()`` function is now officially part of the
  public API of this package.


0.6.0 (2015-10-29)
==================

* Restricted calculation result types to match specification update (removed
  enumeration and enumerationSet).
* Fixed issue where form event failure text was not being checked for the
  default localization.
* Added validation logic to ensure tag identifiers don't collide with page or
  field IDs.
* Added validation logic to ensure tags are unique within an element's list.


0.5.0 (2015-09-25)
==================

* Renamed package to rios.core to follow the rename of the standard from PRISMH
  to RIOS.
* Renamed the ``prismh-validate`` command line tool to ``rios-validate``.


0.4.0 (2015-08-25)
==================

* Added validation logic for the standard widget options.
* Added validation logic for the event options.
* Removed support for Unprompted Fields and Calculate Events in Forms to match
  changes made to the specification.
* Added validation logic that ensures Assessment enumeration values are allowed
  by the Instrument.
* Added validation logic that prevents Form and Interaction Questions from
  describing enumeration values that aren't allowed for the field.
* Added validation of Form subfield configurations.
* Improved the accuracy of the locations reported by some errors.


0.3.0 (2015-06-17)
==================

* Added validation logic to Calculation Sets to make sure calculation IDs don't
  replicate Instrument Field IDs.
* Added validation logic to Calculation Sets that will check to see if Python
  expressions are valid syntax (only enabled on Python 2).
* Added validation logic to Calculation Sets that will check to see if HTSQL
  expressions are valid syntax (only enabled on Python 2 if HTSQL is
  installed).


0.2.1 (2015-06-10)
==================

* Widened the acceptible version range for the ``six`` dependency.


0.2.0 (2015-06-08)
==================

* Added a command line tool, ``prismh-validate``, to perform validations on
  files containing PRIMSH files.
* Expanded format of Web Form event targets to match updated specification.


0.1.1 (2015-05-29)
==================

* Fixed an issue where unprompted fields in Forms weren't being considered when
  verifying field coverage.


0.1.0 (2015-05-29)
==================

* Initial release for review.

