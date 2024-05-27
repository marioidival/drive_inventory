import abc
import base64

from email.mime.text import MIMEText

from drive_inventory import config


class AbstractNotifications(abc.ABC):
    @abc.abstractmethod
    def send(self, to, subject, message):
        raise NotImplementedError


class EmailNotifications(AbstractNotifications):
    def __init__(self, service):
        self.service = service

    def send(self, to, subject, message):
        message = MIMEText(message)
        message["to"] = to
        message["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            self.service.users().messages().send(
                userId="me", body={"raw": raw_message}
            ).execute()
        except Exception as e:
            print(f"failed to send email: {e}")
