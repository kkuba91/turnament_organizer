var app = {
    state: {
        status: false,
        started: false,
        finished: false,
        turnament: { name: '', place: '', players: 0, rounds: 0, actual: 0, system: '', finished: false },
        filelist: [],
        menu_pointer: "block_welcome",
        show_round: 0,
        set_result_data: { round_nr: 0, table_nr: 0, wh_id: 0, wh_plain: '', bl_id: 0, bl_plain: '' },
        previous_view: "block_results",
        players_view_sort: { field: null, direction: 0 },
        players_view_cache: [],
    },

    switchView(request) {
        if (request !== this.state.menu_pointer) {
            var actual = document.getElementById(this.state.menu_pointer);
            var requested = document.getElementById(request);
            if (actual) actual.style.display = "none";
            if (requested) requested.style.display = "block";
            this.state.menu_pointer = request;
        }
    },

    updateStatus() {
        var t_status = document.getElementById("turnament_status");
        var t_started = document.getElementById("turnament_started");
        var b_start = document.getElementById("action-start");
        var b_stop = document.getElementById("action-end");
        var ind_players = document.getElementById("indicator_players");
        var ind_rounds = document.getElementById("indicator_rounds");

        if (this.state.turnament.name) {
            this.state.status = true;
            t_status.textContent = this.state.turnament.name;
            t_status.style.background = "rgba(122,162,247,0.12)";
            t_status.style.color = "var(--accent-primary)";
            t_status.style.borderColor = "rgba(122,162,247,0.3)";
            b_start.disabled = true; b_start.style.display = "none";
            b_stop.disabled = false; b_stop.style.display = "block";
        } else {
            this.state.status = false;
            t_status.textContent = "INACTIVE";
            t_status.style.background = "var(--surface-2)";
            t_status.style.color = "var(--accent-warning)";
            t_status.style.borderColor = "rgba(224,175,104,0.3)";
            t_started.style.display = "none";
            b_start.disabled = false; b_start.style.display = "block";
            b_stop.disabled = true; b_stop.style.display = "none";
            this.switchView("block_welcome");
        }

        this.state.started = this.state.turnament.actual > 0;
        this.state.finished = this.state.turnament.finished;

        if (this.state.status && !this.state.started && !this.state.finished) {
            t_started.textContent = "NOT STARTED";
            t_started.style.display = "inline";
            t_started.style.background = "rgba(224,175,104,0.12)";
            t_started.style.color = "var(--accent-warning)";
            t_started.style.borderColor = "rgba(224,175,104,0.3)";
            this.switchView("block_initial_player_list");
        }
        if (this.state.started && !this.state.finished) {
            t_started.textContent = "IN PROGRESS";
            t_started.style.display = "inline";
            t_started.style.background = "rgba(122,162,247,0.12)";
            t_started.style.color = "var(--accent-primary)";
            t_started.style.borderColor = "rgba(122,162,247,0.3)";
            this.switchView("block_round");
            this.getRound(0);
        }
        if (this.state.started && this.state.finished) {
            t_started.textContent = "FINISHED";
            t_started.style.display = "inline";
            t_started.style.background = "rgba(158,206,106,0.12)";
            t_started.style.color = "var(--accent-success)";
            t_started.style.borderColor = "rgba(158,206,106,0.3)";
            this.switchView("block_results");
            this.getPlayersResults();
        }

        ind_players.textContent = this.state.turnament.players || "0";
        var actual = this.state.turnament.actual || "0";
        var rounds = this.state.turnament.rounds || "0";
        ind_rounds.textContent = actual + " / " + rounds;

        var in_progress = document.getElementById("in_progress");
        var button_rounds = document.getElementById("action_rounds");
        if (this.state.started) {
            in_progress.style.visibility = "visible";
            var buttons = "";
            for (var i = 1; i <= this.state.turnament.actual; i++) {
                var activeClass = (i === this.state.show_round) ? " active" : "";
                buttons += '<button class="btn btn-sidebar' + activeClass + '" onclick="app.showRound(' + i + ')"><i class="bi bi-circle-fill me-2" style="font-size:6px;"></i>Round ' + i + '</button>';
            }
            button_rounds.innerHTML = buttons;
        } else {
            in_progress.style.visibility = "hidden";
        }
        if (this.state.show_round === 0) { this.state.show_round = this.state.turnament.actual; }
    },

    updateView() {
        if (this.state.menu_pointer === "block_initial_player_list") {
            this.getPlayersInit();
        }
    },

    getStatus() {
        fetch("/General/get_status").then(r => r.json()).then(data => {
            if (data.status) {
                this.state.status = data.status;
                this.state.turnament = data.turnament;
                this.state.finished = data.turnament.finished;
            }
            this.updateStatus();
            this.updateView();
        });
    },

    setFile() {
        var name = document.getElementById("turnament_file").value;
        fetch("/Turnament/create?name=" + encodeURIComponent(name), {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(data => {
            this.getStatus();
        });
    },

    getFiles() {
        fetch("/Turnament/get_files", {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(data => {
            var rows = "";
            this.state.filelist = data;
            data.forEach(element => {
                var fname = element.split(".")[0];
                rows += '<tr style="cursor:pointer;" onclick="app.autocompleteDb(\'' + fname + '\')">';
                rows += '<td style="color: var(--text-secondary);"><i class="bi bi-file-earmark me-2"></i>' + element + '</td>';
                rows += '<td style="width:40px;"><button class="btn btn-outline-danger btn-sm" style="padding:2px 6px;font-size:11px;" data-bs-toggle="modal" data-bs-target="#popup_remove_tournament" onclick="event.stopPropagation(); app.removeModal(\'' + element + '\')"><i class="bi bi-trash"></i></button></td>';
                rows += '</tr>';
            });
            document.getElementById("table_rows_files").innerHTML = rows;
        });
    },

    autocompleteDb(fileName) {
        document.getElementById("turnament_file").value = fileName;
    },

    removeModal(element) {
        document.getElementById("removeTournamentLabel").textContent = "Delete tournament '" + element + "' from disk?";
        document.getElementById("remove-files").onclick = function () { app.removeTournament(element); };
    },

    removeTournament(element) {
        fetch("/Turnament/remove_file?tournament_name=" + encodeURIComponent(element), {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(() => { this.getFiles(); });
    },

    closeTurnament() {
        fetch("/Turnament/close", {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(() => {
            this.state.status = false;
            this.state.turnament = { name: '', place: '', players: 0, rounds: 0, actual: 0, system: '', finished: false };
            this.state.show_round = 0;
            this.getStatus();
        });
    },

    addPlayer() {
        var name = document.getElementById("add_p_name").value;
        var surname = document.getElementById("add_p_surname").value;
        var sex = document.getElementById("add_p_sex_female").checked ? "female" : "male";
        var city = document.getElementById("add_p_city").value || "";
        var category = document.getElementById("add_p_category").value || "wc";
        var elo = parseInt(document.getElementById("add_p_elo").value) || 0;
        if (elo > 0 && (elo < 1000 || elo > 3999)) { elo = Math.max(1000, Math.min(3999, elo)); }
        var params = "name=" + encodeURIComponent(name) + "&surname=" + encodeURIComponent(surname) +
            "&sex=" + sex + "&city=" + encodeURIComponent(city) + "&category=" + encodeURIComponent(category) + "&elo=" + elo;
        fetch("/Turnament/turnament/player/add?" + params, {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(() => { this.getStatus(); });
    },

    removePlayer(name, surname) {
        fetch("/Turnament/turnament/player/del?name=" + encodeURIComponent(name) + "&surname=" + encodeURIComponent(surname), {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(() => { this.getStatus(); });
    },

    getPlayersInit() {
        fetch("/Turnament/turnament/players?type=init").then(r => r.json()).then(data => {
            var rows = "";
            var players = data.players.players;
            players.forEach(el => {
                rows += '<tr>';
                rows += '<td class="player-id">' + el.nr + '</td>';
                rows += '<td>' + el.name + '</td>';
                rows += '<td><strong>' + el.surname + '</strong></td>';
                rows += '<td style="color:var(--text-muted);">' + (el.sex === "male" ? '<i class="bi bi-gender-male"></i>' : '<i class="bi bi-gender-female"></i>') + '</td>';
                rows += '<td style="color:var(--text-secondary);">' + el.city + '</td>';
                rows += '<td style="color:var(--text-secondary);">' + (el.club || '') + '</td>';
                var catClass = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(el.cat) ? "badge-cat-high" : "badge-cat-low";
                rows += '<td><span class="badge-cat ' + catClass + '">' + el.cat + '</span></td>';
                rows += '<td style="color:var(--text-secondary);">' + (el.elo > 0 ? el.elo : '-') + '</td>';
                rows += '<td><button class="btn btn-outline-danger btn-sm" style="padding:1px 6px;font-size:11px;" onclick="app.removePlayer(\'' + el.name + '\', \'' + el.surname + '\')"><i class="bi bi-x"></i></button></td>';
                rows += '</tr>';
            });
            document.getElementById("table_rows_players_init").innerHTML = rows;
        });
    },

    getPlayersResults() {
        fetch("/Turnament/turnament/results").then(r => r.json()).then(data => {
            this.switchView("block_results");
            var rows = "";
            var place = 1;
            var players = data.players.players;
            players.forEach(el => {
                var medal = "";
                if (this.state.finished) {
                    if (place === 1) medal = ' <span style="font-size:18px;">🥇</span>';
                    if (place === 2) medal = ' <span style="font-size:18px;">🥈</span>';
                    if (place === 3) medal = ' <span style="font-size:18px;">🥉</span>';
                }
                var catClass = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(el.cat) ? "badge-cat-high" : "badge-cat-low";
                rows += '<tr>';
                rows += '<td><strong>' + place + '</strong>' + medal + '</td>';
                rows += '<td class="player-id">' + el.id + '</td>';
                rows += '<td>' + el.name + '</td>';
                rows += '<td><strong>' + el.surname + '</strong></td>';
                rows += '<td><span class="badge-cat ' + catClass + '">' + el.cat + '</span></td>';
                rows += '<td style="color:var(--text-secondary);">' + (el.elo > 0 ? el.elo : '-') + '</td>';
                rows += '<td><strong>' + el.result + '</strong></td>';
                rows += '<td style="color:var(--text-secondary);">' + el.bucholz + '</td>';
                rows += '<td style="color:var(--text-secondary);">' + el.progress + '</td>';
                rows += '<td><button class="btn btn-outline-secondary btn-sm" style="padding:1px 6px;font-size:11px;" onclick="app.showPlayerStats(' + el.id + ')"><i class="bi bi-bar-chart me-1"></i>Stats</button></td>';
                rows += '</tr>';
                place++;
            });
            document.getElementById("table_rows_players_result").innerHTML = rows;
        });
    },

    showPlayersView() {
        this.state.players_view_sort = { field: null, direction: 0 };
        fetch("/Turnament/turnament/players?type=init").then(r => r.json()).then(data => {
            this.switchView("block_players_view");
            var players = data.players.players.slice();
            players.sort(function (a, b) { return a.id - b.id; });
            this.state.players_view_cache = players;
            this._renderPlayersView(players);
        });
    },

    sortPlayersView(field) {
        var sort = this.state.players_view_sort;
        if (sort.field === field) {
            sort.direction = (sort.direction + 1) % 3;
        } else {
            sort.field = field;
            sort.direction = 1;
        }
        if (sort.direction === 0) { sort.field = null; }

        var players = this.state.players_view_cache.slice();
        var catOrder = ["wc","bk","V","V+","IV","IV+","III","III+","II","II+","II++","I","I+","I++","CM","CM+","CM++","FM","IM","GM"];

        if (sort.field === 'cat') {
            players.sort(function (a, b) {
                var ai = catOrder.indexOf(a.cat);
                var bi = catOrder.indexOf(b.cat);
                return sort.direction === 1 ? bi - ai : ai - bi;
            });
        } else if (sort.field === 'elo') {
            players.sort(function (a, b) {
                return sort.direction === 1 ? b.elo - a.elo : a.elo - b.elo;
            });
        } else {
            players.sort(function (a, b) { return a.id - b.id; });
        }

        this._updateSortIcons();
        this._renderPlayersView(players);
    },

    _updateSortIcons() {
        var sort = this.state.players_view_sort;
        var catIcon = document.getElementById("sort_icon_cat");
        var eloIcon = document.getElementById("sort_icon_elo");
        if (catIcon) {
            catIcon.className = "bi " + (sort.field === 'cat' ? (sort.direction === 1 ? "bi-sort-down" : "bi-sort-up") : "bi-arrow-down-up");
            catIcon.style.opacity = sort.field === 'cat' ? "1" : "0.5";
        }
        if (eloIcon) {
            eloIcon.className = "bi " + (sort.field === 'elo' ? (sort.direction === 1 ? "bi-sort-down" : "bi-sort-up") : "bi-arrow-down-up");
            eloIcon.style.opacity = sort.field === 'elo' ? "1" : "0.5";
        }
    },

    _renderPlayersView(players) {
        var rows = "";
        players.forEach(el => {
            var catClass = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(el.cat) ? "badge-cat-high" : "badge-cat-low";
            rows += '<tr>';
            rows += '<td class="player-id">' + el.id + '</td>';
            rows += '<td>' + el.name + '</td>';
            rows += '<td><strong>' + el.surname + '</strong></td>';
            rows += '<td style="color:var(--text-muted);">' + (el.sex === "male" ? '<i class="bi bi-gender-male"></i>' : '<i class="bi bi-gender-female"></i>') + '</td>';
            rows += '<td style="color:var(--text-secondary);">' + (el.city || '') + '</td>';
            rows += '<td><span class="badge-cat ' + catClass + '">' + el.cat + '</span></td>';
            rows += '<td style="color:var(--text-secondary);">' + (el.elo > 0 ? el.elo : '-') + '</td>';
            rows += '<td><span class="status-badge" style="background:rgba(63,185,80,0.15);color:var(--accent-success);font-size:11px;">Active</span></td>';
            rows += '<td><button class="btn btn-outline-secondary btn-sm" style="padding:1px 6px;font-size:11px;" onclick="app.showPlayerStats(' + el.id + ')"><i class="bi bi-bar-chart me-1"></i>Stats</button></td>';
            rows += '<td><button class="btn btn-outline-primary btn-sm" style="padding:1px 6px;font-size:11px;" data-bs-toggle="modal" data-bs-target="#popup_edit_player" onclick="app.editPlayer(' + el.id + ', \'' + el.name.replace(/'/g, "\\'") + '\', \'' + el.surname.replace(/'/g, "\\'") + '\', \'' + (el.city || '').replace(/'/g, "\\'") + '\', ' + el.elo + ', \'' + el.cat + '\', \'' + el.sex + '\')"><i class="bi bi-pencil me-1"></i>Edit</button></td>';
            rows += '</tr>';
        });
        document.getElementById("table_rows_players_view").innerHTML = rows;
    },

    editPlayer(id, name, surname, city, elo, cat, sex) {
        document.getElementById("edit_p_id").value = id;
        document.getElementById("edit_p_name").value = name;
        document.getElementById("edit_p_surname").value = surname;
        document.getElementById("edit_p_city").value = city;
        document.getElementById("edit_p_elo").value = elo;
        document.getElementById("edit_p_category").value = cat;
        if (sex === "female") {
            document.getElementById("edit_p_sex_female").checked = true;
        } else {
            document.getElementById("edit_p_sex_male").checked = true;
        }
    },

    savePlayerEdit() {
        var id = document.getElementById("edit_p_id").value;
        var name = document.getElementById("edit_p_name").value;
        var surname = document.getElementById("edit_p_surname").value;
        var city = document.getElementById("edit_p_city").value || "";
        var elo = parseInt(document.getElementById("edit_p_elo").value) || 0;
        if (elo > 0 && (elo < 1000 || elo > 3999)) { elo = Math.max(1000, Math.min(3999, elo)); }
        var category = document.getElementById("edit_p_category").value || "wc";
        var sex = document.getElementById("edit_p_sex_female").checked ? "female" : "male";
        var params = "player_id=" + id + "&name=" + encodeURIComponent(name) + "&surname=" + encodeURIComponent(surname) +
            "&city=" + encodeURIComponent(city) + "&elo=" + elo + "&category=" + encodeURIComponent(category) + "&sex=" + sex;
        fetch("/Turnament/turnament/player/edit?" + params, {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(() => {
            this.showPlayersView();
        });
    },

    showPlayerStats(playerId) {
        this.state.previous_view = this.state.menu_pointer;
        fetch("/Turnament/turnament/player/stats?player_id=" + playerId).then(r => r.json()).then(data => {
            this.switchView("block_player_stats");
            var p = data.player;
            document.getElementById("player_stats_title").textContent = p.name + " " + p.surname;
            document.getElementById("stat_points").textContent = p.points.toFixed(1);
            document.getElementById("stat_elo").textContent = p.elo || "-";
            document.getElementById("stat_elo_change").textContent = (p.elo_change >= 0 ? "+" : "") + p.elo_change.toFixed(1);
            document.getElementById("stat_elo_change").style.color = p.elo_change >= 0 ? "var(--accent-success)" : "var(--accent-danger)";
            document.getElementById("stat_bucholz").textContent = p.bucholz.toFixed(1);

            var rows = "";
            p.rounds.forEach(function (r) {
                var resultBadge = "";
                if (r.result === 1.0) resultBadge = '<span class="badge-result badge-win">1.0</span>';
                else if (r.result === 0.5) resultBadge = '<span class="badge-result badge-draw">½</span>';
                else if (r.result === 0.0) resultBadge = '<span class="badge-result badge-loss">0.0</span>';
                else resultBadge = '<span style="color:var(--text-muted);">-</span>';

                var colorIcon = r.color === "white" ? '<span style="display:inline-block;width:12px;height:12px;background:#fff;border-radius:2px;border:1px solid var(--border-default);"></span>' :
                    '<span style="display:inline-block;width:12px;height:12px;background:#000;border-radius:2px;border:1px solid var(--border-default);"></span>';

                var eloChange = r.elo_change !== 0 ? ((r.elo_change >= 0 ? "+" : "") + r.elo_change.toFixed(1)) : "-";
                var eloColor = r.elo_change > 0 ? "var(--accent-success)" : (r.elo_change < 0 ? "var(--accent-danger)" : "var(--text-muted)");

                rows += '<tr>';
                rows += '<td>' + r.round_nr + '</td>';
                rows += '<td>' + (r.opponent_name || 'Bye') + '</td>';
                rows += '<td style="color:var(--text-secondary);">' + (r.opponent_elo > 0 ? r.opponent_elo : '-') + '</td>';
                rows += '<td>' + colorIcon + '</td>';
                rows += '<td>' + resultBadge + '</td>';
                rows += '<td style="color:' + eloColor + ';">' + eloChange + '</td>';
                rows += '</tr>';
            });
            document.getElementById("table_player_stats_rounds").innerHTML = rows;
        });
    },

    goBack() {
        this.switchView(this.state.previous_view);
    },

    showRound(nr) {
        if (this.state.started) {
            this.state.show_round = nr;
            this.switchView("block_round");
            this.getRound(nr);
        }
        this.updateRoundVisibility();
    },

    getRound(round) {
        fetch("/Round/turnament/round/get_results?nr=" + round + "&full=true").then(r => r.json()).then(data => {
            var rows = "";
            var tables = data.round.tables;
            var roundNr = data.round.nr;

            tables.forEach(element => {
                var wh = element.white;
                var bl = element.black;

                var whCat = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(wh.cat) ? "badge-cat-high" : "badge-cat-low";
                var blCat = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(bl.cat) ? "badge-cat-high" : "badge-cat-low";

                var whResult = "", blResult = "";
                if (element.result === '1.0/0.0') { whResult = '<span class="badge-result badge-win">+1</span>'; blResult = '<span class="badge-result badge-loss">+0</span>'; }
                else if (element.result === '0.0/1.0') { whResult = '<span class="badge-result badge-loss">+0</span>'; blResult = '<span class="badge-result badge-win">+1</span>'; }
                else if (element.result === '0.5/0.5') { whResult = '<span class="badge-result badge-draw">½</span>'; blResult = '<span class="badge-result badge-draw">½</span>'; }

                rows += '<tr>';
                rows += '<td class="player-id">' + element.nr + '</td>';
                rows += '<td><span class="player-id me-1">#' + wh.id + '</span> <span class="badge-cat ' + whCat + ' me-1">' + wh.cat + '</span> <strong>' + wh.surname + ' ' + wh.name + '</strong>';
                if (wh.elo > 1000) rows += ' <span style="color:var(--text-muted);font-size:11px;">' + wh.elo + '</span>';
                rows += ' ' + whResult + '</td>';
                rows += '<td style="color:var(--text-muted);text-align:center;">vs</td>';
                rows += '<td><span class="player-id me-1">#' + bl.id + '</span> <span class="badge-cat ' + blCat + ' me-1">' + bl.cat + '</span> <strong>' + bl.surname + ' ' + bl.name + '</strong>';
                if (bl.elo > 1000) rows += ' <span style="color:var(--text-muted);font-size:11px;">' + bl.elo + '</span>';
                rows += ' ' + blResult + '</td>';
                rows += '<td style="color:var(--text-secondary);">' + element.result + '</td>';

                if (this.state.started && this.state.show_round === this.state.turnament.actual && !this.state.finished) {
                    var whPlain = '#' + wh.id + ' ' + wh.surname + ' ' + wh.name;
                    var blPlain = '#' + bl.id + ' ' + bl.surname + ' ' + bl.name;
                    rows += '<td><button class="btn btn-outline-primary btn-sm" style="padding:1px 6px;font-size:11px;" data-bs-toggle="modal" data-bs-target="#popup_set_result" onclick="app.setForResult(\'' + roundNr + '\', \'' + element.nr + '\', \'' + whPlain.replace(/'/g, "\\'") + '\', \'' + wh.id + '\', \'' + blPlain.replace(/'/g, "\\'") + '\', \'' + bl.id + '\')"><i class="bi bi-pencil"></i></button></td>';
                } else {
                    rows += '<td></td>';
                }
                rows += '</tr>';
            });

            document.getElementById("table_rows_round").innerHTML = rows;
            document.getElementById("view_round_val").textContent = "Round " + roundNr + ":";

            // Pauser info
            var infoBox = document.getElementById("round_info_box");
            var pauserEl = document.getElementById("view_pauser");
            var suspendedEl = document.getElementById("view_suspended");
            pauserEl.innerHTML = "";
            suspendedEl.innerHTML = "";
            var showInfo = false;

            if (data.round.pauser && typeof data.round.pauser === 'object') {
                var p = data.round.pauser;
                var pCat = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(p.cat) ? "badge-cat-high" : "badge-cat-low";
                pauserEl.innerHTML = '<i class="bi bi-pause-circle me-1" style="color:var(--accent-warning);"></i><strong>Bye:</strong> <span class="player-id me-1">#' + p.id + '</span> <span class="badge-cat ' + pCat + ' me-1">' + p.cat + '</span> <strong>' + p.surname + ' ' + p.name + '</strong> (+1 pt)';
                showInfo = true;
            }
            if (data.round.suspended && data.round.suspended.length > 0) {
                var html = '<i class="bi bi-person-dash me-1" style="color:var(--accent-danger);"></i><strong>Suspended:</strong> ';
                data.round.suspended.forEach(function (s) {
                    var sCat = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(s.cat) ? "badge-cat-high" : "badge-cat-low";
                    html += '<span class="player-id me-1">#' + s.id + '</span> <span class="badge-cat ' + sCat + ' me-1">' + s.cat + '</span> ' + s.surname + ' ' + s.name + ' &nbsp; ';
                });
                suspendedEl.innerHTML = html;
                showInfo = true;
            }
            infoBox.style.display = showInfo ? "block" : "none";

            this.updateRoundVisibility();
        });
    },

    updateRoundVisibility() {
        var btns = document.getElementById("buttons_act_round");
        var next_button_vis = "hidden";
        var isCurrentActiveRound = (this.state.show_round === this.state.turnament.actual && !this.state.finished);
        btns.style.display = isCurrentActiveRound ? "inline-flex" : "none";

        var nextBtn = document.getElementById("btn_next_round");
        if (nextBtn) {
            if (this.state.turnament.actual >= this.state.turnament.rounds) {
                nextBtn.innerHTML = '<i class="bi bi-flag-fill me-1"></i> Finish Tournament';
            } else {
                nextBtn.innerHTML = '<i class="bi bi-arrow-right me-1"></i> Next Round';
            }
        }
        var printBtn = document.getElementById("show_round_html");
        if (printBtn) {
            var sr = this.state.show_round;
            printBtn.onclick = function () { app.showRoundPrintView(sr); };
        }
        if (isCurrentActiveRound) { next_button_vis = "visible"; } else { next_button_vis = "hidden"; }
        btns.style.visibility = next_button_vis;
    },

    startTournament() {
        var rounds = document.getElementById("start_t_rounds").value;
        var system = document.getElementById("start_t_system").value;
        fetch("/Turnament/turnament/start?rounds=" + rounds + "&system_type=" + system, {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(() => { location.reload(); });
    },

    setForResult(roundNr, tableNr, whPlain, whId, blPlain, blId) {
        this.state.set_result_data = { round_nr: roundNr, table_nr: tableNr, wh_id: whId, wh_plain: whPlain, bl_id: blId, bl_plain: blPlain };
        document.getElementById("popup_set_result_round").textContent = " " + roundNr;
        document.getElementById("popup_set_result_table").textContent = " " + tableNr;
        document.getElementById("popup_set_result_wh").innerHTML = '<span style="color:var(--text-primary);">' + whPlain + '</span>';
        document.getElementById("popup_set_result_bl").innerHTML = '<span style="color:var(--text-primary);">' + blPlain + '</span>';
    },

    setWin() { this._setResult(1.0); },
    setDraw() { this._setResult(0.5); },
    setLoose() { this._setResult(0.0); },
    setNothing() { this._setResult(-1.0); },

    _setResult(result) {
        fetch("/Round/turnament/round/set_result?table_nr=" + this.state.set_result_data.table_nr + "&result=" + result, {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(() => { this.getStatus(); });
    },

    nextRound() {
        fetch("/Round/turnament/round/apply_results", {
            method: "POST", headers: { "Content-Type": "application/json" }
        }).then(r => r.json()).then(data => {
            if (data === true || data.status === true) {
                location.reload();
            } else {
                this.getStatus();
            }
        });
    },

    showRoundPrintView(round) {
        fetch("/Round/turnament/round/get_results/html?nr=" + round + "&full=true").then(r => r.text()).then(html => {
            var blob = new Blob([html], { type: "text/html" });
            var url = URL.createObjectURL(blob);
            var tab = window.open(url, "_blank");
            if (!tab) {
                var printFrame = document.createElement("iframe");
                printFrame.style.display = "none";
                document.body.appendChild(printFrame);
                printFrame.contentDocument.open();
                printFrame.contentDocument.write(html);
                printFrame.contentDocument.close();
                printFrame.contentWindow.focus();
                printFrame.contentWindow.print();
                setTimeout(function () { document.body.removeChild(printFrame); }, 1000);
            }
        });
    },

    printResults() {
        var table = document.getElementById("results_table");
        if (!table) return;
        var html = '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Results</title>';
        html += '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">';
        html += '<style>body{padding:20px;font-size:13px;}@media print{.no-print{display:none;}}</style></head><body>';
        html += '<h4>Tournament Results</h4>';
        html += '<table class="table table-sm table-bordered">' + table.innerHTML + '</table>';
        html += '<div class="no-print mt-3"><button class="btn btn-sm btn-outline-dark" onclick="window.print()">Print</button></div>';
        html += '</body></html>';
        var blob = new Blob([html], { type: "text/html" });
        var url = URL.createObjectURL(blob);
        var tab = window.open(url, "_blank");
        if (!tab) {
            var printFrame = document.createElement("iframe");
            printFrame.style.display = "none";
            document.body.appendChild(printFrame);
            printFrame.contentDocument.open();
            printFrame.contentDocument.write(html);
            printFrame.contentDocument.close();
            printFrame.contentWindow.focus();
            printFrame.contentWindow.print();
            setTimeout(function () { document.body.removeChild(printFrame); }, 1000);
        }
    },

    loadSuspendList() {
        fetch("/Turnament/turnament/players/suspend_list").then(r => r.json()).then(data => {
            var rows = "";
            data.players.forEach(function (p) {
                var checked = p.suspended ? ' checked' : '';
                var catClass = ["CM", "CM+", "CM++", "FM", "IM", "GM"].includes(p.cat) ? "badge-cat-high" : "badge-cat-low";
                rows += '<tr>';
                rows += '<td><input type="checkbox" class="form-check-input suspend-checkbox" data-player-id="' + p.id + '"' + checked + '></td>';
                rows += '<td class="player-id">' + p.id + '</td>';
                rows += '<td>' + p.surname + ' ' + p.name + '</td>';
                rows += '<td><span class="badge-cat ' + catClass + '">' + p.cat + '</span></td>';
                rows += '</tr>';
            });
            document.getElementById("table_suspend_players").innerHTML = rows;
        });
    },

    applySuspensions() {
        var checkboxes = document.querySelectorAll('.suspend-checkbox');
        var suspended = [];
        var unsuspended = [];
        checkboxes.forEach(function (cb) {
            var pid = parseInt(cb.getAttribute("data-player-id"));
            if (cb.checked) { suspended.push(pid); }
            else { unsuspended.push(pid); }
        });
        fetch("/Turnament/turnament/players/suspend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ suspended: suspended, unsuspended: unsuspended })
        }).then(r => r.json()).then(() => {
            this.getRound(this.state.show_round);
        });
    }
};

document.addEventListener("DOMContentLoaded", function () {
    app.getStatus();
});
