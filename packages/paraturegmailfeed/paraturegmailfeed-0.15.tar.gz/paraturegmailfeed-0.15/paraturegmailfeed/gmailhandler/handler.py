"""Module containing GmailHandler class. The class abstracts working with
the Gmail Api Client. Methods were taken from sample code and adopted for
use in the GmailHandler class.
"""


import httplib2
import logging

from apiclient import discovery, errors

from authentication import Authentication


class GmailHandler(object):
    """Class abstracts working with the Gmail Api Client"""
    def __init__(self, config):
        print config
        if 'CLIENT_SECRET_FILE' not in config:
            raise Exception
        client_secret_file = config['CLIENT_SECRET_FILE']

        if 'SCOPES' not in config:
            raise Exception
        scopes = config['SCOPES']

        if 'APPLICATION_NAME' not in config:
            raise Exception
        application_name = config['APPLICATION_NAME']

        self.authentication = Authentication(client_secret_file, application_name, scopes)

        self.service = self._build_service()

    def _build_service(self):
        """Build Gmail Api Client discovery service"""
        # Build credentials
        credentials = self.authentication.get_credentials()
        http = credentials.authorize(httplib2.Http())
        # Build service
        service = discovery.build('gmail', 'v1', http=http)

        return service

    def get_message(self, user_id, msg_id):
        """Get a Message with given ID.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

        Returns:
        A Message.
        """
        try:
            message = self.service.users().messages().get(userId=user_id, id=msg_id).execute()

        except errors.HttpError, error:
            #logger.critical("GmailApiClient error: " + str(error))
            pass
        else:
            return message

    def list_messages_matching_query(self, user_id, query=''):
        """List all Messages of the user's mailbox matching the query.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

        Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
        """
        try:
            response = self.service.users().messages().list(userId=user_id,
                                                   q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId=user_id, q=query,
                                             pageToken=page_token).execute()
                messages.extend(response['messages'])
        except errors.HttpError, error:
            #logger.critical("GmailApiClient error: " + str(error))
            pass
        else:
            return messages

    def list_messages_with_labels(self, user_id, label_ids=[]):
        """List all Messages of the user's mailbox with label_ids applied.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        label_ids: Only return Messages with these labelIds applied.

        Returns:
        List of Messages that have all required Labels applied. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate id to get the details of a Message.
        """
        try:
            response = self.service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.service.users().messages().list(userId=user_id,
                                                     labelIds=label_ids,
                                                     pageToken=page_token).execute()
                messages.extend(response['messages'])

        except errors.HttpError, error:
            #logger.critical("GmailApiClient error: " + str(error))
            pass
        else:
            return messages

    def modify_message(self, user_id, msg_id, msg_labels):
        """Modify the Labels on the given Message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The id of the message required.
        msg_labels: The change in labels.

        Returns:
        Modified message, containing updated labelIds, id and threadId.
        """
        try:
            message = self.service.users().messages().modify(userId=user_id, id=msg_id,
                                                body=msg_labels).execute()

            label_ids = message['labelIds']

            #logger.info('MODIFIED Message ID: %s - With Label IDs %s' % (msg_id, label_ids))
        except errors.HttpError, error:
            #logger.critical("GmailApiClient error: " + str(error))
            print str(error)
        else:
            return message

    def list_labels(self, user_id):
        """Get a list all labels in the user's mailbox.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.

        Returns:
        A list all Labels in the user's mailbox.
        """
        try:
            response = self.service.users().labels().list(userId=user_id).execute()
            labels = response['labels']
            #for label in labels:
            #    print 'Label id: %s - Label name: %s' % (label['id'], label['name'])
        except errors.HttpError, error:
            #logger.critical("GmailApiClient error: " + str(error))
            pass
        else:
            return labels

    @staticmethod
    def create_message_labels():
        """Create object to update labels.

        Returns:
        A label update object.
        """
        return {'removeLabelIds': ['Label_14'], 'addLabelIds': ['Label_13']}
