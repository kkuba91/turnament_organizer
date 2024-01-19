# Turnament Organizer
Chess turnament organizer (construct concept).

Lightweight tool for smart player pairing in swiss system.

## Generals
- target: ``weekend project``
- layer structured application with builder pattern :rage3:

## Actual Status
- it is on stage  ``PROOF OF CONCEPT``
- simple pairing order: ``1) points`` ``2) bucholz`` ``3) progress``
- command line API  ``DEPRICATED``
- REST API  ``Fast API``
- platforms  ``Linux`` ``Windows``
- logging ``DEBUG (forced)`` ``console``

## Targets
- [must have] support swiss system matching for all rounds of defined with all rules - ✔
- [need have] swiss system should match players that they have as similar opponent ranks as it is possible - ✔
- [need to have] single elimination (round Robin) and circular systems - x
- [must have] results sort with dynamic defined preferences - x
- [optional] gui layer with some third party module used or REST API - ✔
- [optional] save data to db/text files (save data) - ✔
- [optional] load data from saved files - ✔
- [optional] save data to excel with all rounds dump - x

## Launch
Main launcher in `runner.py`.
``` bash
$ python3 runner.py
```
or
``` bash
$ py -3 runner.py
```
