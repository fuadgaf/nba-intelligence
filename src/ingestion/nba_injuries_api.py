"""Official NBA injury report client (via the nbainjuries package).

Runs locally and needs Java installed (the package reads the report PDFs with tabula-py).
Saves raw JSON for upload to the bronze UC Volume.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from nbainjuries import injury


class NbaInjuriesApi:
    """Pulls official NBA injury report snapshots and saves them as JSON files."""

    def __init__(self, output_dir: str | Path = "data/raw/nba_injuries") -> None:
        self.output_dir = Path(output_dir)

    def get_report(self, report_time: datetime) -> list[dict]:
        """The injury report snapshot published at `report_time` (US Eastern time).

        TODO: check the function name and return type against the nbainjuries README.
        """
        data = injury.get_reportdata(report_time)
        return json.loads(data) if isinstance(data, str) else data

    def save_raw(self, data: list[dict], name: str) -> Path:
        """Save raw JSON as <output_dir>/<name>_<UTC timestamp>.json."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"{name}_{stamp}.json"
        path.write_text(json.dumps(data))
        return path


if __name__ == "__main__":
    # manual test: uv run python src/ingestion/nba_injuries_api.py
    api = NbaInjuriesApi()
    report = api.get_report(datetime(2026, 11, 26, 17, 30))  # pick a recent report time
    print(f"{len(report)} rows")
    print(api.save_raw(report, "injury_report"))
