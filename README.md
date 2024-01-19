[![Version: 0.2.0](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/kkuba91/turnament_organizer)
[![Platform: win / linux](https://img.shields.io/badge/platform-win/linux-orange)](https://github.com/kkuba91/turnament_organizer)

# Turnament Organizer
Chess turnament organizer (construct concept).

Lightweight tool for smart player pairing in swiss system.

## Generals
- target: ``weekend project``
- layer structured application with builder pattern :rage3:

## Actual Status
- it is on stage  ``PROOF OF CONCEPT`` ``0.2.0``
- simple pairing order: ``1) points`` ``2) bucholz`` ``3) progress``
- command line API  ``DEPRICATED``
- REST API  ``Fast API``
- platforms  ``Linux`` ``Windows``
- logging ``DEBUG (forced)`` ``console``

## Targets
- [must have] support swiss system matching for all rounds of defined with all rules - ✔
- [need have] swiss system should match players with similar opponent ranks/points - ✔
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

## Quick Manual
After the `Launch` run in cmd/bash console, open web browser on location: `http://127.0.0.1:8000/`. In the window suppose to load a welcomepage:

![alt text]([https://github.com/kkuba91/uGESRTP/blob/main/Example%20-%20Rich/Screenshot1.png?raw=true](https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/WelcomeView.png)https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/WelcomeView.png)
