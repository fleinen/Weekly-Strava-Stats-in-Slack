from datetime import datetime
import requests
from bs4 import BeautifulSoup
import logging
from weekly_strava_stats.storage.week_stats import WeekStats


class StravaConnector:
    def __init__(self, widget_url):
        self.widget_url = widget_url

    def fetch_strava_widget_data(self):
        """
        Fetch and parse Strava widget data

        Returns:
        dict: Containing runs, distance, time, and elevation
        """
        try:
            response = requests.get(self.widget_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })

            runs = 0
            distance = 0.0
            time = 0.0
            elevation = 0

            soup = BeautifulSoup(response.text, 'html.parser')
            stats_list = soup.find('ul', class_='list-stats content')
            stat_items = stats_list.find_all('li')
            for item in stat_items:
                stat_subtext = item.find('span', class_='stat-subtext').text.strip().lower()
                stat_text = item.find('b', class_='stat-text').text.strip()

                if 'runs' in stat_subtext:
                    runs = int(stat_text)
                elif 'distance' in stat_subtext:
                    distance = float(stat_text.split()[0])
                elif 'time' in stat_subtext:
                    time_parts = stat_text.split()
                    hours = 0
                    minutes = 0
                    if 'h' in time_parts[0]:
                        hours = int(time_parts[0].replace('h', ''))
                        if len(time_parts) > 1:
                            minutes = int(time_parts[1].replace('m', ''))
                    else:
                        minutes = int(time_parts[0].replace('m', ''))
                    time = hours * 60 + minutes
                elif 'elevation' in stat_subtext:
                    elevation = int(stat_text.split()[0])

            # get year, week number
            date_range = soup.find('h2', class_='compact').text.strip()
            start_date = datetime.strptime(date_range.split('-')[0].split('of ')[-1].strip(), "%b %d, %Y")
            year = start_date.year
            week_number = start_date.isocalendar()[1]

            return WeekStats(
                year=year,
                week_number=week_number,
                runs=runs,
                distance=distance,
                time=time,
                elevation=elevation
            )

        except Exception as e:
            logging.error(f"Error fetching Strava widget data: {e}")
            exit(1)
