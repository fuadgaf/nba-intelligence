"""NBA.com stats client (via the nba_api package).

Runs locally only: stats.nba.com blocks cloud IPs, including Databricks and GitHub Actions.
Saves raw JSON for upload to the bronze UC Volume.
"""

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nba_api.stats.endpoints import playergamelog


class NbaDataApi:
    """Pulls raw stats from stats.nba.com and saves them as JSON files."""

    def __init__(
        self,
        output_dir: str | Path = "data/raw/nba_stats",
        timeout: int = 30,
        sleep_seconds: float = 1.0,
        max_retries: int = 3,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.timeout = timeout
        self.sleep_seconds = sleep_seconds  # NBA.com throttles fast requests
        self.max_retries = max_retries

    def _call(self, endpoint_cls: type, **params: Any) -> dict:
        """Call an nba_api endpoint with a simple retry, and return its raw JSON."""
        for attempt in range(1, self.max_retries + 1):
            try:
                result = endpoint_cls(**params, timeout=self.timeout).get_dict()
                time.sleep(self.sleep_seconds)
                return result
            except Exception as exc:
                print(f"Attempt {attempt}/{self.max_retries} failed: {exc}")
                if attempt == self.max_retries:
                    raise
                time.sleep(self.sleep_seconds * attempt * 2)
        raise RuntimeError("unreachable")

    def get_player_game_log(self, player_id: int, season: str = "2026-27") -> dict:
        """One player's game log for a season."""
        return self._call(playergamelog.PlayerGameLog, player_id=player_id, season=season)

    def save_raw(self, data: dict, name: str) -> Path:
        """Save raw JSON as <output_dir>/<name>_<UTC timestamp>.json."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"{name}_{stamp}.json"
        path.write_text(json.dumps(data))
        return path


if __name__ == "__main__":
    # manual test: uv run python src/ingestion/nba_data_api.py
    api = NbaDataApi()
    data = api.get_player_game_log(player_id=1630595)  # Cade Cunningham
    print(api.save_raw(data, "player_game_log_1630595"))
