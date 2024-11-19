import logging
import os
import click
from dotenv import load_dotenv

from weekly_strava_stats.storage import WeekStatsStorage
from weekly_strava_stats.strava import StravaConnector
from weekly_strava_stats.slack import SlackChannelConnector
from weekly_strava_stats.utils import MessageBuilder, get_app_data_dir, setup_logging


def initialize_app():
    """Set up logging and load environment variables"""
    setup_logging(get_app_data_dir() / 'weekly_strava_stats.log')
    load_dotenv()


@click.group()
def cli():
    """Strava Slack Integration CLI"""
    pass


@cli.command()
def fetch_strava_stats():
    """Fetch Strava statistics and save to file"""
    initialize_app()
    logging.info("Fetching Strava statistics")

    # Validate inputs
    widget_url = os.getenv('STRAVA_WIDGET_URL')
    if not widget_url:
        logging.error("Strava widget URL not provided")
        return

    # Determine stats file path
    stats_file = get_app_data_dir() / 'strava_stats.json'

    # Fetch stats
    strava_connector = StravaConnector(widget_url)
    stats = strava_connector.fetch_strava_widget_data()

    # Save stats
    strava_stats_storage = WeekStatsStorage(stats_file)
    strava_stats_storage.save_weekly_stats(stats)


@cli.command()
def post_last_weeks_stats():
    """Post Strava statistics to Slack"""
    initialize_app()
    logging.info("Posting last week's Strava statistics to Slack'")

    # Validate inputs
    slack_token = os.getenv('SLACK_BOT_TOKEN')
    if not slack_token:
        click.echo("Error: Slack Bot Token not provided", err=True)
        return

    slack_channel = os.getenv('SLACK_CHANNEL')
    if not slack_channel:
        click.echo("Error: Slack Channel not provided", err=True)
        return

    # Determine stats file path
    strava_stats_file = get_app_data_dir() / 'strava_stats.json'

    # Load and post stats
    strava_stats_storage = WeekStatsStorage(strava_stats_file)

    last_weeks_stats = strava_stats_storage.load_weekly_stats(-1)
    compare_stats = strava_stats_storage.load_weekly_stats(-2)
    if last_weeks_stats is None:
        logging.error("No stats found for last week")
        return

    groq_api_key = os.getenv('GROQ_API_KEY')
    strava_club_url = os.getenv('STRAVA_CLUB_URL')
    message_builder = MessageBuilder(groq_api_key, strava_club_url)
    message = message_builder.build(last_weeks_stats, compare_stats)

    slack_connector = SlackChannelConnector(slack_token, slack_channel)
    slack_connector.post_message(slack_channel, message)


if __name__ == '__main__':
    cli()
