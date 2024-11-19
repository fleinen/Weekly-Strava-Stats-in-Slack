from typing import Optional
from weekly_strava_stats.storage.week_stats import WeekStats


class MessageBuilder:
    @staticmethod
    def build(stats: WeekStats, last_week_stats: Optional[WeekStats] = None) -> str:
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

        return "\n".join(message_lines)

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
