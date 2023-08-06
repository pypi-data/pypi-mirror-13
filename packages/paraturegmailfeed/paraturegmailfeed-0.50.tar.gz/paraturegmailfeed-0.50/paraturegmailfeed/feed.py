# feed.py
"""Module containing feed.
"""


import logging
import os

from paraturegmailfeed.config import Config
from paraturegmailfeed.gmailhandler import GmailHandler
from paraturegmailfeed.mongodao import MongoDao
from paraturegmailfeed.paratureaction import ParatureAction

# LOG_CONFIG['level'] = logging.DEBUG
# logging.basicConfig(**LOG_CONFIG)


class ParatureGmailFeed(object):
    """The ParatureGmailFeed implements a feed that fetches messages from
    the Gmail API, transforms the messages, parses them for pertintent data,
    and loads them into a MongoDB database.
    """

    # The class that is used to load configuration
    config_class = Config

    # The class that is used to connect and work with Gmail API
    gmail_handler_class = GmailHandler

    root_path = os.getcwd()
    db = None

    def __init__(self, config_filepath):
        self.config = self.config_class(self.root_path)
        self.config.from_pyfile(config_filepath)
        self.db = MongoDao(self.config['MONGO_URI'], self.config['DB_NAME'])

    def run(self):
        """Run the feed"""
        handler = self.gmail_handler_class(self.config)

        user_id = self.config['USER_ID']
        target_label = self.config['TARGET_LABEL_QUERY']

        # Fetch list of messages ids
        message_list = handler.list_messages_matching_query(user_id, target_label)
        message_ids = [msg['id'] for msg in message_list]

        for msg_id in message_ids:
            gmail_message = handler.get_message(user_id, msg_id)
            action = ParatureAction(gmail_message)

            self.db.save('action', action.to_dict())

            # Modify message (apply 'Processed' label)
            message_labels = handler.create_message_labels()
            handler.modify_message(user_id, msg_id, message_labels)
