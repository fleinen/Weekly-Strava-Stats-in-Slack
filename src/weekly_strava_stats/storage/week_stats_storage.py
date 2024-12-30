import logging
from weekly_strava_stats.storage import WeekStats
import json
from pathlib import Path
from typing import List, Optional
from dataclasses import asdict
from datetime import datetime


class WeekStatsStorage:
    """
    Handles storing and loading StravaStats
    """
    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)

    def _load_all_stats(self) -> List[WeekStats]:
        """
        Load all stats from the storage file
        """
        if not self.storage_path.exists():
            return []

        with self.storage_path.open('r') as f:
            stats_list = json.load(f)

        return [WeekStats(**stats) for stats in stats_list]

    def _save_all_stats(self, stats: List[WeekStats]):
        """
        Save all stats to the storage file
        """
        stats_list = [asdict(stat) for stat in stats]
        with self.storage_path.open('w') as f:
            json.dump(stats_list, f)

    def save_weekly_stats(self, stats: WeekStats):
        """
        Save the weekly stats to the storage file.
        If stats for the same week already exist, they will be overwritten.
        """
        all_stats = self._load_all_stats()
        # Remove existing entry with the same year and week_number
        all_stats = [s for s in all_stats if not (s.year == stats.year and s.week_number == stats.week_number)]
        all_stats.append(stats)
        self._save_all_stats(all_stats)
        logging.info(f"Saved weekly stats for {stats.year} week {stats.week_number} to {self.storage_path}")

    def load_weekly_stats(self, relative_week_number: int) -> Optional[WeekStats]:
        """
        Load the stats for a week relative to the current week.

        Args:
            relative_week_number (int): The number of weeks to go back. 0 for the current week, -1 for last week, etc.

        Returns:
            Optional[StravaStats]: The stats for the requested week. None if the stats are not found.
        """
        now = datetime.now()
        current_year = now.isocalendar()[0]
        current_week_number = now.isocalendar()[1]

        target_week_number = current_week_number + relative_week_number
        target_year = current_year

        while target_week_number <= 0:
            target_week_number += 52
            target_year -= 1

        while target_week_number > 52:
            target_week_number -= 52
            target_year += 1

        return self._load_weekly_stats(target_year, target_week_number)

    def _load_weekly_stats(self, year: int, week_number: int) -> Optional[WeekStats]:
        """
        Load the weekly stats for a given year and week number.
        Returns None if the stats are not found.
        """
        all_stats = self._load_all_stats()
        for stats in all_stats:
            if stats.year == year and stats.week_number == week_number:
                return stats
        return None
