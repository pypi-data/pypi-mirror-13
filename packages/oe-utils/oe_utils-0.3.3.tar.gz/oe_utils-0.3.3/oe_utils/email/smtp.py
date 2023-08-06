# -*- coding: utf-8 -*-
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from pyramid.compat import text_


class SMTPClient:
    def __init__(self, smpt, sender):
        '''
            :param smtp: Simple Mail Transfer Protocol (SMTP) to send mails
            :param sender: Sender of the mail
        '''
        self.smtp = smpt
        self.sender = sender

    @property
    def smtp_obj(self):  # pragma no cover
        return smtplib.SMTP(self.smtp)

    def send_mail(self, receivers, subject, message):
        '''

        send an email

        :param sender: Sender
        :param receivers: Receivers (list)
        :param subject: Email subject
        :param message: Email message
        '''
        message_mime = MIMEText(message, _charset="UTF-8")
        message_mime['Subject'] = Header(subject, "utf-8")
        message_mime['From'] = Header(text_(self.sender), "utf-8")
        message_mime['To'] = Header(text_('; '.join(receivers)), "utf-8")
        self.smtp_obj.sendmail(self.sender, receivers, message_mime.as_string())
