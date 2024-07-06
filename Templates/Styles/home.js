function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
  }

var app = new Vue({
    el: "#app",
    data: {
        title: 'Turnament Ogranizer',
        status: false,
        started: false,
        finished: false,
        turnament: {
            name: '',
            place: '',
            players: 0,
            rounds: 0,
            actual: 0,
            system: '',
            finished: false
        },
        filelist: [],
        menu_pointer: "block_welcome",
        playerlist: [],
        set_result_data: {
            round_nr: 0,
            table_nr: 0,
            wh_id: 0,
            wh_plain: '',
            bl_id: 0,
            bl_plain: '',
        },
        show_round: 0,
    },
    methods: {
        switchView(request) {
            if (request != this.menu_pointer) {
                console.log("View: " + this.menu_pointer + " -> " + request);
                actual_view = document.getElementById(this.menu_pointer);
                requested_view = document.getElementById(request);
                requested_view.style.display = "block";
                this.menu_pointer = request; 
                actual_view.style.display = "none";
            }
        },
        updateView() {
            if (this.menu_pointer == "block_initial_player_list") {
                this.getPlayersInit();
            }
        },
        updateStatus() {
            // a_open = document.getElementById("action_open");
            t_status = document.getElementById("turnament_status");
            t_started = document.getElementById("turnament_started");
            b_start = document.getElementById("action-start");
            b_stop = document.getElementById("action-end");
            ind_players = document.getElementById("indicator_players");
            ind_rounds = document.getElementById("indicator_rounds");
            if(this.turnament.name){
                this.status = true;
                t_status.className = "text-success-emphasis";
                t_status.textContent = this.turnament.name;
                b_start.disabled = true; b_start.style.display = "none";
                b_stop.disabled = false; b_stop.style.display = "block";
            } else {
                this.status = false;
                t_status.className = "text-warning";
                t_status.textContent = "INACTIVE";
                t_started.style.visibility = "hidden";
                b_start.disabled = false; b_start.style.display = "block";
                b_stop.disabled = true; b_stop.style.display = "none";
                this.switchView("block_welcome");
            }
            this.started = this.turnament.actual > 0;
            if(this.status && ~this.started && ~this.finished){
                t_started.className = "text-warning";
                t_started.textContent = "UNSTARTED";
                t_started.style.visibility = "visible";
                this.switchView("block_initial_player_list");
            }
            if(this.started && ~this.finished){
                t_started.className = "text-primary-emphasis";
                t_started.textContent = "IN PROGRESS";
                t_started.style.visibility = "visible";
                this.switchView("block_round");
                this.getRound(0);
            }
            if(this.started && this.finished){
                t_started.className = "text-success-emphasis";
                t_started.textContent = "FINISHED";
                t_started.style.visibility = "visible";
                this.switchView("block_results");
                this.getPlayersResults();
            }
            ind_players.innerHTML = this.turnament.players | "0";
            var actual = this.turnament.actual | "0";
            var rounds = this.turnament.rounds | "0";
            ind_rounds.innerHTML = ""+actual+" / "+rounds;

            var in_progress = document.getElementById("in_progress");
            var button_rounds = document.getElementById("action_rounds");
            if(this.started) {
                in_progress.style.visibility = "visible";
                var buttons = "";
                for (let i = 1; i < this.turnament.actual+1; i++) {
                    buttons += '<button class="btn btn-primary btn-sm" id="action-rounds" onclick="app.showRound('+i+')">Round '+i+'</button>';
                  }
                  button_rounds.innerHTML = buttons;
            } else { in_progress.style.visibility = "hidden"; }
            if (this.show_round == 0) { this.show_round = this.turnament.actual; }
        },
        showRoundPrintView(round) {
            console.log("triggered: " + round);
            axios.get("/Round/turnament/round/get_results/html?nr="+round+"&full=true", {
                nr: round,
                full: true
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    var tab = window.open("data:text/html," + encodeURIComponent(response.data), "_blank");
                    tab.document.write(response.data);
                    tab.focus();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        showRound(nr) {
            if (this.started) {
                if (nr == 0) {nr = this.actual;}
                this.show_round = nr;
                this.switchView("block_round");
                this.getRound(nr);
            }
        },
        autocompleteDb(fileName) {
            var input_filed = document.getElementById("turnament_file");
            input_filed.value = fileName;
            console.log(fileName)
        },
        getStatus() {
            axios.get("/General/get_status", {}, {
                headers: { 'Content-type': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    if(response.data.status){
                        this.status = response.data.status;
                        this.turnament = response.data.turnament;
                        this.finished = response.data.turnament.finished;
                    }
                    this.updateStatus();
                    console.log("status: " + response.data.status);
                    console.log("turnament: " + response.data.turnament);
                    console.log("finished: " + this.finished);
                    this.updateView();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        setFile() {
            var name = document.getElementById("turnament_file").value
            axios.post("/Turnament/create?name=" + name, {
                name: name,
                path: ""
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    if(response.turnament){
                        this.data.turnament = response.data.turnament;
                        this.finished = response.data.turnament.finished;
                    }
                    turnament = "\nTurnament:\n+ name: " + response.data.turnament.name + "\n+ place: " + response.data.turnament.place + "\n+ players: " + response.data.turnament.players  + "\n+ rounds: " + response.data.turnament.rounds + "\n+ actual: " + response.data.turnament.actual + "\n+ finished: " + response.data.turnament.finished + "\n+ system: " + response.data.turnament.system;
                    console.log("\nstatus: " + response.data.status);
                    console.log(turnament);
                } else {
                    console.log("ERROR: " + response.status);
                }
                this.getStatus();
            });
        },
        getFiles() {
            axios.post("/Turnament/get_files", {
                path: ""
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                var rows = "";
                if(response.status == "200"){
                    console.log(response.data);
                    this.filelist = response.data;
                    this.filelist.forEach(element => {
                        rows += '<tr><th class="text-secondary-emphasis" onclick="app.autocompleteDb(\''+element.split(".")[0]+'\')"><i>'+element+'</i></th>';
                        rows += '<th class="text-danger-emphasis d-grid gap-2"><button class="btn btn-outline-danger btn-sm" type="button" data-bs-toggle="modal" data-bs-target="#popup_remove_tournament" onclick="app.removeModal(\''+element+'\')"><i class="bi bi-trash"></i></button></th></tr>';
                    });
                    document.getElementById("table_rows_files").innerHTML = rows;
                } else {
                    console.log("ERROR: " + response.status);
                }
                this.getStatus();
            });
        },
        removeModal(element) {
            console.log("removeModal: " + element)
            var removeTournamentLabel = document.getElementById("removeTournamentLabel");
            removeTournamentLabel.textContent = "Remove tournament \'" + element + "\' files from disk?";
            var removeFiles = document.getElementById("remove-files");
            removeFiles.outerHTML
            removeFiles.onclick = function() { app.removeTournament(element); }
        },
        removeTournament(element) {
            console.log("removeTournament: " + element)
            axios.post("/Turnament/remove_file?tournament_name=" + element, {
                tournament_name:element
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log(response.data);
                } else {
                    console.log("ERROR: " + response.status);
                }
                this.getFiles();
            });
            
        },
        closeTurnament() {
            axios.post("/Turnament/close", {
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log(response.data);
                } else {
                    console.log("ERROR: " + response.status);
                }
                this.status = false;
                this.turnament = {};
                this.getStatus();
            });
        },
        addPlayer() {
            var name = document.getElementById("add_p_name").value;
            var surname = document.getElementById("add_p_surname").value;
            var sex = "male"
            if (document.getElementById("add_p_sex_male").checked && ~document.getElementById("add_p_sex_female").checked) { sex = "male"; } else { sex = "female"; }
            var city = document.getElementById("add_p_city").value;
            var category = document.getElementById("add_p_category").value;
            var elo = document.getElementById("add_p_elo").value;
            city = city || "";
            category = category || "wc";
            elo = elo || 0;
            axios.post("/Turnament/turnament/player/add?name=" + name + "&surname=" + surname + "&sex=" + sex + "&city=" + city + "&category=" + category + "&elo=" + elo, {
                name: name,
                surname: surname,
                sex: sex,
                city: city,
                category: category,
                elo: elo
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log("Add Player Success!");
                } else {
                    console.log("ERROR: " + response.status);
                }
                this.getStatus();
            });
        },
        removePlayer(name, surname) {
            axios.post("/Turnament/turnament/player/del?name=" + name + "&surname=" + surname, {
                name: name,
                surname: surname
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log("Remove Player "+name+surname+" Success!");
                } else {
                    console.log("ERROR: " + response.status);
                }
                this.getStatus();
            });
        },
        getPlayersInit() {
            axios.get("/Turnament/turnament/players?type=init", {
                type: "init"
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                var rows = "";
                if(response.status == "200"){
                    console.log(response.data);
                    this.playerlist = response.data.players.players;
                    this.playerlist.forEach(element => {
                        rows += '<tr><th class="text-secondary-emphasis"><i>'+element.nr+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.name+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.surname+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.sex+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.city+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.club+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.cat+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.elo+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><span class="badge bg-danger-subtle border border-danger-subtle text-danger-emphasis rounded-2" onclick="app.removePlayer(\''+element.name+'\', \''+element.surname+'\')"><i class="bi bi-person-x"></i></span></th>'
                        rows += "</tr>";
                    });
                    document.getElementById("table_rows_players_init").innerHTML = rows;
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        getPlayersResults() {
            axios.get("/Turnament/turnament/results", {
                type: "results"
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                this.switchView("block_results");
                var rows = "";
                var place = 1;
                var place_mark = "";
                var gender_sign = "";
                if(response.status == "200"){
                    console.log(response.data);
                    this.playerlist = response.data.players.players;
                    this.playerlist.forEach(element => {
                        place_mark = "";
                        if ( place == 1 && this.finished ) { place_mark = " 🥇"; }
                        if ( place == 2 && this.finished ) { place_mark = " 🥈"; }
                        if ( place == 3 && this.finished ) { place_mark = " 🥉"; }
                        if ( element.sex == "male" ) { gender_sign = '<i class="fa fa-mars" aria-hidden="true"></i>'; } else { gender_sign = '<i class="fa fa-venus" aria-hidden="true"></i>'; }
                        rows += '<tr><th class="text-secondary-emphasis"><i>'+place+'</i> '+place_mark+'</th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.id+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.name+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.surname+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+gender_sign+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.city+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.club+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.cat+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.elo+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.result+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.bucholz+'</i></th>';
                        rows += '<th class="text-secondary-emphasis"><i>'+element.progress+'</i></th>';
                        rows += "</tr>";
                        place += 1;
                    });
                    document.getElementById("table_rows_players_result").innerHTML = rows;
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        getRound(round) {
            axios.get("/Round/turnament/round/get_results?nr="+round+"&full=true", {
                nr: round,
                full: true
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                var rows = "";
                var pauser_block = "";

                var win = '<span class="badge bg-success-subtle border border-success-subtle text-success-emphasis rounded-2">+1.0</span>';
                var draw = '<span class="badge bg-warning-subtle border border-warning-subtle text-warning-emphasis rounded-2">+½</span>';
                var loose = '<span class="badge bg-danger-subtle border border-danger-subtle text-danger-emphasis rounded-2">+0.0</span>';

                var span_elo = "";
                var cat_title = "is-warning";
                if(response.status == "200"){
                    console.log(response.data);
                    var tables = response.data.round.tables;
                    tables.forEach(element => {
                        var wh = element.white;
                        var bl = element.black;
                        var addons_start = '<div>';
                        var addons_end = '</div>';
                        var wh_result = '<span class="badge bg-light-subtle border border-primary-subtle text-primary-emphasis rounded-2">'+wh.result+' </span> ';
                        var bl_result = '<span class="badge bg-light-subtle border border-primary-subtle text-primary-emphasis rounded-2">'+bl.result+' </span> ';
                        if (element.result == '1.0/0.0') { wh_result = wh_result+win; bl_result = bl_result+loose; }
                        if (element.result == '0.0/1.0') { wh_result = wh_result+loose; bl_result = bl_result+win; }
                        if (element.result == '0.5/0.5') { wh_result = wh_result+draw; bl_result = bl_result+draw; }
                        rows += '<tr><th class="text-secondary-emphasis">'+addons_start+'<span class="badge bg-light-subtle border border-light-subtle text-light-emphasis rounded-2">'+element.nr+'</span></th>'

                        if (["wc", "bk", "V", "IV", "III", "II", "I"].includes(wh.cat)) { cat_title = "bg-light-subtle"; } else { cat_title = "bg-warning-subtle text-warning-emphasis"; }
                        if (wh.elo > 1000) { span_elo = '<span class="badge bg-light-subtle border border-light-subtle text-light-emphasis rounded-2">'+wh.elo+'</span> '; } else { span_elo = ''; }
                        rows += '<th class="text-secondary-emphasis"><span class="">#'+wh.id+'</span> <span class="badge border border-light-subtle text-light-emphasis rounded-2 '+cat_title+'">'+wh.cat+'</span> ';
                        rows += '<span class=""><strong>'+wh.surname+' '+wh.name+'</strong></span> '+span_elo+wh_result+' </th>';

                        rows += '<th class="text-secondary-emphasis">vs.</th>';

                        if (["wc", "bk", "V", "IV", "III", "II", "I"].includes(bl.cat)) { cat_title = "bg-light-subtle"; } else { cat_title = "bg-warning-subtle text-warning-emphasis"; }
                        if (bl.elo > 1000) { span_elo = '<span class="badge bg-light-subtle border border-light-subtle text-light-emphasis rounded-2">'+bl.elo+'</span> '; } else { span_elo = ''; }
                        rows += '<th class="text-secondary-emphasis"><span class="">#'+bl.id+'</span> <span class="badge border border-light-subtle text-light-emphasis rounded-2 '+cat_title+'">'+bl.cat+'</span> ';
                        rows += '<span class=""><strong>'+bl.surname+' '+bl.name+'</strong></span> '+span_elo+bl_result+' </th>';

                        rows += '<th class="text-secondary-emphasis"><span>'+element.result+'</span>';

                        if ( this.started && this.show_round == this.turnament.actual && this.finished == false ){
                            var round_nr = response.data.round.nr;
                            var wh_plain = '#'+wh.id+' ['+wh.cat+'] '+wh.surname+' '+wh.name;
                            var bl_plain = '#'+bl.id+' ['+bl.cat+'] '+bl.surname+' '+bl.name;
                            rows += '  <button id="round_modifier" type="button" class="badge bg-primary border border-light-subtle text-light-emphasis p-1" data-bs-toggle="modal" data-bs-target="#popup_set_result" onclick="app.setForResult(\''+round_nr+'\', \''+element.nr+'\', \''+wh_plain+'\', \''+wh.id+'\', \''+bl_plain+'\', \''+bl.id+'\')"><i class="bi bi-pencil-square"></i></button>';
                        }
                        
                        rows += addons_end+'</th><th class="text-secondary-emphasis"></th></tr>'
                    });
                    document.getElementById("table_rows_round").innerHTML = rows;
                    if ( response.data.round.pauser ) {
                        var pauser = response.data.round.pauser;
                        if (["bk","wc", "V", "IV", "III", "II", "I"].includes(pauser.cat)) {
                            cat_title = "badge bg-light-subtle border border-light-subtle text-light-emphasis rounded-2";
                        } else {
                            cat_title = "badge bg-warning-subtle border border-warning-subtle text-warning-emphasis rounded-2";
                        }
                        pauser_block += 'Pauser: <span>#'+pauser.id+'</span> <span class="'+cat_title+'">'+pauser.cat+'</span> '
                        if (pauser.elo > 1000) { span_elo = '<span class="badge bg-light-subtle border border-light-subtle text-light-emphasis rounded-2">'+pauser.elo+'</span>'; } else { span_elo = ''; }
                        pauser_block += '<span><strong>'+pauser.surname+' '+pauser.name+'</strong></span> '+span_elo;
                        document.getElementById("view_pauser").innerHTML = pauser_block+' (+1 point)';
                    }
                    document.getElementById("view_round_val").innerHTML = 'Round '+response.data.round.nr+':';
                    this.updateVisibility();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        startTournament() {
            var t_rounds = document.getElementById("start_t_rounds").value;
            var t_system = document.getElementById("start_t_system").value;
            axios.post("/Turnament/turnament/start?rounds="+t_rounds+"&system_type="+t_system, {
                rounds: t_rounds,
                system_type: t_system
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    this.status = response.data.status;
                    this.turnament = response.data.turnament;
                    this.getStatus();
                } else {
                    console.log("ERROR: " + response.status);
                }
                document.location.reload();
            });
        },
        setForResult(round_nr, table_nr, wh_plain, wh_id, bl_plain, bl_id) {
            console.info("Round: "+round_nr+", Table: "+table_nr);
            console.info(wh_plain+" vs "+bl_plain);
            this.set_result_data.round_nr = round_nr;
            this.set_result_data.table_nr = table_nr;
            this.set_result_data.wh_id = wh_id;
            this.set_result_data.wh_plain = wh_plain;
            this.set_result_data.bl_id = bl_id;
            this.set_result_data.bl_plain = bl_plain;
            document.getElementById("popup_set_result").classList.add('is-active');
            document.getElementById("popup_set_result_round").innerHTML = " "+this.set_result_data.round_nr;
            document.getElementById("popup_set_result_table").innerHTML = " "+this.set_result_data.table_nr;
            document.getElementById("popup_set_result_wh").innerHTML = '<span>'+this.set_result_data.wh_plain+'</span>';
            document.getElementById("popup_set_result_bl").innerHTML = '<span>'+this.set_result_data.bl_plain+'</span>';
        },
        setWin() {
            axios.post("/Round/turnament/round/set_result?table_nr="+this.set_result_data.table_nr+"&result=1.0", {
                table_nr: this.set_result_data.table_nr,
                result: 1.0
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log("Win OK");
                    this.getStatus();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        setDraw() {
            axios.post("/Round/turnament/round/set_result?table_nr="+this.set_result_data.table_nr+"&result=0.5", {
                table_nr: this.set_result_data.table_nr,
                result: 0.5
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log("Draw OK");
                    this.getStatus();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        setLoose() {
            axios.post("/Round/turnament/round/set_result?table_nr="+this.set_result_data.table_nr+"&result=0.0", {
                table_nr: this.set_result_data.table_nr,
                result: 0.0
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log("Loose OK");
                    this.getStatus();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        setNothing() {
            axios.post("/Round/turnament/round/set_result?table_nr="+this.set_result_data.table_nr+"&result=-1.0", {
                table_nr: this.set_result_data.table_nr,
                result: -1.0
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == "200"){
                    console.log("Nothing OK");
                    this.getStatus();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        nextRound() {
            axios.post("/Round/turnament/round/apply_results", {
            }, {
                headers: { 'Content-type': 'application/json', 'accept': 'application/json',}
            }).then((response) => {
                if(response.status == 200){
                    console.log("Results OK");
                    this.getStatus();
                    document.location.reload();
                } else {
                    console.log("ERROR: " + response.status);
                }
            });
        },
        updateVisibility() {
        // VISIBILITY LOGIC:
        var next_button_vis = "hidden";
        var show_round = Number(this.show_round);
        if (this.show_round == this.turnament.actual && this.finished == false) { next_button_vis = "visible"; } else { next_button_vis = "hidden"; }
        console.log("act_round: "+this.turnament.actual+"\nshow:"+this.show_round+"\nfinished:"+this.finished)
        document.getElementById("buttons_act_round").style.visibility = next_button_vis;
        show_round_html = document.getElementById("show_round_html");
        console.log(show_round)
        show_round_html.onclick = function() { app.showRoundPrintView(show_round); }
        }
    }
});
document.addEventListener("DOMContentLoaded", function() {
        app.getStatus();
    });
