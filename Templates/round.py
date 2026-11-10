"""round.py

Round view static page generator class.

"""

import logging
from pathlib import Path

TABLE_ROW = """
                                <tr>
                                    <td><span class="badge border border-secondary-emphasis text-secondary">{table_nr}</span></td>
                                    <td><span class="badge border border-secondary-emphasis text-secondary">#{w_player_nr}</span>
                                        <span class="badge border border-secondary-emphasis text-secondary">{w_player_cat}</span>
                                        <span class="text-secondary">{w_player_surname} {w_player_name}</span>
                                        <span class="text-secondary"><i> {w_player_elo}</i></span></td>
                                    <td><span class="badge border border-secondary-emphasis text-secondary">#{b_player_nr}</span>
                                        <span class="badge border border-secondary-emphasis text-secondary">{b_player_cat}</span>
                                        <span class="text-secondary">{b_player_surname} {b_player_name}</span>
                                        <span class="text-secondary"><i> {b_player_elo}</i></span></td>
                                    <td> {table_result}</td>
                                </tr>
    """
INFO_VIEW = """
                <div class="card d-grid gap-0 my-3 border-secondary-subtle">
                    <div class="card-header text-light py-0 text-secondary-emphasis"><i class="bi bi-info-circle me-2"> </i>Info</div>
                    <div class="card-body">
                        <!-- PAUSER -->
                        <!-- FUTURE_SUSPENDED -->
                        <!-- SUSPENDED -->
                    </div>
                </div>
    """
PAUSER = """
                        Pauser: <span class="badge border border-secondary-emphasis text-secondary">#{player_nr}</span>
                        <span class="badge border border-secondary-emphasis text-secondary">{player_cat}</span>
                        <span class="text-secondary">{player_surname} {player_name}</span>
                        <span class="text-secondary"><i> {player_elo}</i></span>
    """
FUTURE_SUSPENDED = """
                        <p>Future suspended: <span class="badge border border-secondary-emphasis text-secondary">#{player_nr}</span>
                        <span class="badge border border-secondary-emphasis text-secondary">{player_cat}</span>
                        <span class="text-secondary">{player_surname} {player_name}</span>
                        <span class="text-secondary"><i> {player_elo}</i></span>
                        {player_plays_until}</p>
    """
SUSPENDED = """
                        <p><span class="badge border border-secondary-emphasis text-secondary">#{player_nr}</span>
                        <span class="badge border border-secondary-emphasis text-secondary">{player_cat}</span>
                        <span class="text-secondary">{player_surname} {player_name}</span>
                        <span class="text-secondary"><i> {player_elo}</i></span>
                        {player_plays_in}</p>
    """


class RoundView(object):
    def __init__(self, data: dict = None) -> None:
        self._template_name = "round.html"
        self.destination_name = ""
        self.data = data
        status = bool(self.data and self.data.get("status", False))
        self.print_round = self.data["round"]["nr"] if status else None
        self._tables = self.data["round"]["tables"] if status else None
        self._pauser = (
            self.data["round"]["pauser"]
            if status and self.data["round"].get("pauser", False)
            else None
        )
        self._suspended = (
            self.data["round"]["suspended"]
            if status and self.data["round"].get("suspended", False)
            else None
        )
        self._future_suspended = (
            self.data["round"]["future_suspended"]
            if status and self.data["round"].get("future_suspended", False)
            else None
        )
        print("PAUSER:", self._pauser, "SUSPENDED:", self._suspended)
        # Load template from module directory (not cwd)
        template_path = Path(__file__).parent / "round.html"
        with open(template_path) as template:
            self._template = template.read()

    def update(self):
        # Update filename
        self._update_dest_name()

        # Update content
        self._update_line(
            template_str="Round ## out of ##", new_str=f"Round {self.print_round}"
        )
        self._add_player_rows()
        self._update_info()

    def _update_dest_name(self):
        """Update filename"""
        self.destination_name = f"round_{self.print_round}.html"

    def _add_player_rows(self):
        """Update content - player tables"""
        rows = ""
        for table in self._tables:
            rows += TABLE_ROW.format(
                table_nr=table["nr"],
                w_player_nr=table["white"]["id"],
                w_player_cat=table["white"]["cat"],
                w_player_name=table["white"]["name"],
                w_player_surname=table["white"]["surname"],
                w_player_elo=table["white"]["elo"] if table["white"]["elo"] > 0 else "",
                b_player_nr=table["black"]["id"],
                b_player_cat=table["black"]["cat"],
                b_player_name=table["black"]["name"],
                b_player_surname=table["black"]["surname"],
                b_player_elo=table["black"]["elo"] if table["black"]["elo"] > 0 else "",
                table_result=table["result"],
            )
        self._template = self._template.replace("<!-- ROWS -->", rows)

    def _update_info(self):
        """Update content - extra info about Pauser or suspended Players"""
        if self._pauser or self._future_suspended or self._suspended:
            self._template = self._template.replace("<!-- INFO -->", INFO_VIEW)
            if self._pauser:
                pauser = PAUSER.format(
                    player_nr=self._pauser["id"],
                    player_cat=self._pauser["cat"],
                    player_name=self._pauser["name"],
                    player_surname=self._pauser["surname"],
                    player_elo=self._pauser["elo"] if self._pauser["elo"] > 0 else "",
                )
                self._template = self._template.replace("<!-- PAUSER -->", pauser)
            if self._future_suspended:
                future_suspended = "Future suspended: "
                for player in self._future_suspended:
                    plays_until = player.get("plays_until")
                    player_plays_until = (
                        f'<span class="text-secondary" style="font-size:12px;">'
                        f"(plays until round {plays_until} end)</span>"
                        if plays_until
                        else ""
                    )
                    row = FUTURE_SUSPENDED.format(
                        player_nr=player["id"],
                        player_cat=player["cat"],
                        player_name=player["name"],
                        player_surname=player["surname"],
                        player_elo=player["elo"] if player["elo"] > 0 else "",
                        player_plays_until=player_plays_until,
                    )
                    future_suspended += row
                self._template = self._template.replace(
                    "<!-- FUTURE_SUSPENDED -->", future_suspended
                )
            if self._suspended:
                suspended = "Suspended: "
                for player in self._suspended:
                    plays_in = player.get("plays_in")
                    player_plays_in = (
                        f'<span class="text-secondary" style="font-size:12px;">'
                        f"(plays in round {plays_in})</span>"
                        if plays_in
                        else ""
                    )
                    row = SUSPENDED.format(
                        player_nr=player["id"],
                        player_cat=player["cat"],
                        player_name=player["name"],
                        player_surname=player["surname"],
                        player_elo=player["elo"] if player["elo"] > 0 else "",
                        player_plays_in=player_plays_in,
                    )
                    suspended += row
                self._template = self._template.replace("<!-- SUSPENDED -->", suspended)

    def _update_line(self, template_str="", new_str=""):
        updated = ""
        for line in self._template.splitlines():
            if template_str in line:
                line = line.replace(template_str, new_str)
            updated += line + "\n"
        self._template = updated
        return updated


if __name__ == "__main__":
    msg_comment = "RoundView class for creating static html files representing round with pairing."
    logging.info(msg=msg_comment)
