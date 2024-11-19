from dataclasses import dataclass


@dataclass
class WeekStats:
    """
    A class to represent statistics from Strava activities.

    Attributes:
        year (int): Year of the statistics.
        week (int): Week number of the year.
        runs (int): Number of runs.
        distance (float): Total distance covered in kilometers.
        time (float): Total time spent running in minutes.
        elevation (int): Total elevation gain in meters.
    """
    year: int
    week_number: int
    runs: int  # Number of runs
    distance: float  # Distance in km
    time: float  # Time in minutes
    elevation: int  # Elevation in meters
