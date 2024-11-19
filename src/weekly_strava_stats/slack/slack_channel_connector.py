from slack_bolt import App
import logging


class SlackChannelConnector:
    def __init__(self, token, channel):
        self.token = token
        self.channel = channel
        self.app = App(token=self.token)

    def post_message(self, channel, message):
        try:
            response = self.app.client.chat_postMessage(
                channel=channel,
                text=message
            )
            logging.info(f"Message sent to Slack: {response}")

        except Exception as e:
            logging.error(f"Error sending Slack message: {e}")
            exit(1)
