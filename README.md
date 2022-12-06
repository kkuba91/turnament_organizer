# Turnament Organizer
Chess turnament organizer (short construct concept). It is my hobby app I want to write to support lightweight tool for smart round matching in swiss system.

## Actual Status
- it is just a beginning  ``ALWAYS``
- only command line API  ``IN PROGRESS``
- ~~only first round for swiss system (under debug/deployment)~~  ``INITIAL VERSION``
- no target time - hobby in my free time ``ALWAYS``
- layer structured application with builder pattern :rage3:

## Targets
- [must have] support swiss system matching for all rounds of defined with all rules [✔ / 🚧 ]
- [need have] swiss systm should match players that They have as similar opponent ranks as it is possible [✔]
- [need to have] single elimination and circular systems [ ]
- [must have] results sort with dynamic defined preferences [ ]
- [optional] gui layer with some third party module used or REST API [ ]
- [optional] save data to text files (dump data) [ ]
- [optional] load data from saved files [ ]
- [optional] save data to excel with all rounds dump [ ]

## Launch
Main launcher in `runner.py`.
``` bash
$ python3 runner.py
```
or
``` bash
$ py -3 runner.py
```
