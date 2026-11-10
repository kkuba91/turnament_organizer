## 0.4.0

- Add 'suspended' functionalities - to mark player suspended from the next round.
- Add edit buttons for added Players to the next round.
- Add remove button to suspended players.
- Fix 'many words' tournament name (until now only one word was allowed).
- Add optional element 'Club' for player data.
- Add disable for 'Add player' button if non-filled form is and similar for Round view when not all results filled.
- Fix issue with unproper calculations (double, miscalculated, etc.) when in-progress tournament is closed and reopened.
- Fix issue with unproper 'Bye' calculations and missing frontend appearance with the data for 'Bye'.
- Change some frontend behaviours with autocomplete values in dropdown lists (remove it) and showing modals after removing tournament.
- Add optional element 'Federation' for player data. 

## 0.3.0

- Add `Players` view with the list
- Add `Player` view with details and results
- Add possibility to add Players to the next round and suspend them from the next Round
- Change app style to be quite like `Tokyo Night` theme
- Set CLI sturtup entrypoint to `turnament-organizer` for easier use
- Move to template-based dynamic rendering using `Jinja2`

## 0.2.1

- Change code to Python module and run as `turnament-organizer` CLI entrypoint

## 0.2.1

- Moved UI to `Bootstrap` © styling
- Add easy print version of Round View
- Fix some bugs with resetting table result in db
- Add Tournament remove possiblility
- Change storage representation related to tournament as separate dot-directories
- Add UI placeholder buttons to suspend/add Players during events (non-functioning yet!)
- Fulfill license (to emphaze it has NO commercial restrinctions as well)

## 0.2.0

- Initial version with any web UI on `Bulma` © styling ✨💪
- Backend on `FastAPI` ©
- Frontend on `pure` 😥 (rather poor 😅) `HTML`
