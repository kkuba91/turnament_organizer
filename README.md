[![Version: 0.2.0](https://img.shields.io/badge/version-0.2.0-blue)](https://github.com/kkuba91/turnament_organizer)
[![Platform: win / linux](https://img.shields.io/badge/platform-win/linux-orange)](https://github.com/kkuba91/turnament_organizer)
![GitHub License](https://img.shields.io/github/license/kkuba91/turnament_organizer)


# Turnament Organizer
Lightweight tool for smart player pairing in swiss system.

## Generals
- in two words ``weekend project``
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
or (on Windows):
``` bash
$ py -3 runner.py
```

## Quick Manual
After the `Launch` run in cmd/bash console, open web browser on location: `http://127.0.0.1:8000/`.

In the window suppose to load a welcomepage:

![alt text](https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/WelcomeView.png)

To begin click `OPEN`. Select existing file (just point and click right one on the list) or type new one name. Than click `Set Tournament File`. As on presented below screenshot.

![alt text](https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/CreateOpenFile.png)

Now it is a moment to add players who are going to play in the tournament. Note, that tournament indicator in the top-left cornr changed. Add players one-by-one by `[+]` and than apply to start clicking `START TOURNAMENT`.

![alt text](https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/AddPlayerTable.png)

In showed popup set quantity of rounds to play and pairing system.
> [!WARNING]\
> Actual version supports only swiss systm!

![alt text](https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/StartTournamentPopup.png)

When tournament is started, simply fill up results of right tables. To approve round result, click `Next Round`.

![alt text](https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/SettingResults.png)

When the last round is about to end and the last result is filled, also approve round by `Next Round`. Than final results table will show.

![alt text](https://raw.githubusercontent.com/kkuba91/turnament_organizer/frontend/.screenshots/0.2.0/ResultsFinished.png)

## Third Party packages
- Fast API for rest api - [![Fast API](https://img.shields.io/badge/-Fast%20API-grey?logo=github)](https://github.com/tiangolo/fastapi)
- Bulma for frontend CSS style standard - [![Bulma](https://img.shields.io/badge/-Bulma-grey?logo=github)](https://github.com/jgthms/bulma)

