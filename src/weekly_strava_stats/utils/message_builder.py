import random
from typing import Optional
from weekly_strava_stats.storage.week_stats import WeekStats
from groq import Groq
from importlib import resources
import weekly_strava_stats


class MessageBuilder:
    def __init__(self, groq_api_key: Optional[str]):
        """
        Initialize the MessageBuilder with the given GROQ API key.

        Args:
            groq_api_key (Optional[str]): The API key for accessing the GROQ service. Can be None if not required.
        """
        self.groq_api_key = groq_api_key

    def build(self, stats: WeekStats, last_week_stats: Optional[WeekStats] = None) -> str:
        """
        Builds a message string containing the current week's statistics and a quote.

        Args:
            stats (WeekStats): The statistics for the current week.
            last_week_stats (Optional[WeekStats], optional): The statistics for the previous week. Defaults to None.

        Returns:
            str: A message string containing the current week's statistics and a quote.
        """
        message = MessageBuilder.get_stats_message(stats, last_week_stats)
        message += "\n\n" + self.get_quote(original_message=message)

        return message

    @staticmethod
    def get_stats_message(stats: WeekStats, last_week_stats: Optional[WeekStats] = None) -> str:
        """
        Generate a weekly running stats message for Slack.

        Args:
            stats (StravaStats): Current week's running statistics.
            last_week_stats (Optional[StravaStats], optional): Previous week's running statistics. Defaults to None.

        Returns:
            str: Formatted message with running stats and comparison.
        """
        stats_items = [
            ("Runs", stats.runs, last_week_stats.runs if last_week_stats else None),
            ("Distance", stats.distance, last_week_stats.distance if last_week_stats else None, "km"),
            ("Time", stats.time, last_week_stats.time if last_week_stats else None, "minutes"),
            ("Elevation", stats.elevation, last_week_stats.elevation if last_week_stats else None, "meters")
        ]

        message_lines = [f"🏃 Weekly Running Stats for week {stats.week_number}/{stats.year}"]
        if last_week_stats:
            message_lines[0] += " (compared to last week)"

        for item in stats_items:
            stat_name, current_value, previous_value, *unit = item
            unit = unit[0] if unit else ""

            line = f"• {stat_name}: {current_value} {unit}".rstrip()

            if previous_value is not None:
                line += f" ({MessageBuilder.format_stat_diff(current_value, previous_value)})"

            message_lines.append(line)

        message = "\n".join(message_lines)
        return message

    @staticmethod
    def get_trend_emoji(value: float, prev_value: float) -> str:
        """
        Determine the trend emoji based on the value change.

        Args:
            value (float): Current value.
            prev_value (float): Previous value.

        Returns:
            str: Emoji representing the trend.
        """
        if value > prev_value:
            return '📈'
        if value < prev_value:
            return '📉'
        return '＝'

    @staticmethod
    def format_stat_diff(value: float, prev_value: float) -> str:
        """
        Format the difference between current and previous values.

        Args:
            value (float): Current value.
            prev_value (float): Previous value.

        Returns:
            str: Formatted difference string with trend emoji.
        """
        diff = abs(value - prev_value)
        percentage = (diff / prev_value)
        trend_emoji = MessageBuilder.get_trend_emoji(value, prev_value)

        return f"{trend_emoji} {percentage:.0%}"

    def get_quote(self, original_message: str) -> str:
        """
        Retrieves a quote. If the `groq_api_key` is not set, it returns a default quote.
        Otherwise, it generates a quote using the `groq_api_key`.

        Returns:
            str: The retrieved or generated quote.
        """
        if not self.groq_api_key:
            return MessageBuilder.get_default_quote()
        return MessageBuilder.get_generated_quote(self, original_message)

    def get_generated_quote(self, original_message: str) -> str:
        """
        Generates a quote based on the provided original message and a randomly selected prompt configuration.
        Args:
            original_message (str): The original message to be included in the prompt for generating the quote.
        Returns:
            str: A generated quote formatted with the author's name and the quote in italics.
        """
        with resources.path(weekly_strava_stats, 'data') as data_dir:
            quotes_path = data_dir / "quote_prompts.csv"

        with open(quotes_path, 'r') as quotes_file:
            # read without header (first line)
            prompt_configs = quotes_file.readlines()[1:]

        prompt_config = random.choice(prompt_configs)
        author, user_prompt, language = prompt_config.split(';')

        full_prompt = f"I provide you the aggregated running stats of our running group and I want you to come up with a quote to comment on it that sounds like it's from {author} {user_prompt}. Just reply with the quote in {language}, no explanation or quotation marks around it."
        full_prompt += f"\n\n{original_message}"

        groq_client = Groq(api_key=self.groq_api_key)
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": full_prompt,
                }
            ],
            model="llama-3.2-90b-text-preview"
        )
        fake_quote = chat_completion.choices[0].message.content
        message = f"{author}: _{fake_quote}_"
        return message

    @staticmethod
    def get_default_quote() -> str:
        """
        Retrieves a random quote from a predefined list of quotes stored in a text file.

        Returns:
            str: A randomly selected quote from the quotes file.
        """
        with resources.path(weekly_strava_stats, 'data') as data_dir:
            quotes_path = data_dir / "quotes.txt"

        with open(quotes_path, 'r') as quotes_file:
            default_quotes = quotes_file.readlines()

        return f"_{random.choice(default_quotes)}_"
