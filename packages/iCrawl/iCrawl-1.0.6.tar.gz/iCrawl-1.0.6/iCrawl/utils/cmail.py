#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import base64
import smtplib

from email import Encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, send_to, subject, text, files=[],
              server=None, user=None, password=None, usessl=True):

    assert type(send_to) == list
    assert type(files) == list

    msg = MIMEMultipart('alternative')
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text, 'plain', 'utf-8'))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    if user is not None:
        smtp.ehlo()
        if usessl is True:
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
        else:
            smtp_userid64 = base64.encodestring(user)
            smtp.docmd("auth", "login " + smtp_userid64[:-1])
            if password is not None:
                smtp_pass64 = base64.encodestring(password)
                smtp.docmd(smtp_pass64[:-1])

    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


def send_html_mail(send_from, send_to, subject, text, html_text, files=[],
                   server=None, user=None, password=None, usessl=True):

    assert type(send_to) == list
    assert type(files) == list

    msg = MIMEMultipart('alternative')
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    if text is not None and len(text) > 0:
        msg.attach(MIMEText(text, 'plain', 'utf-8'))

    msg.attach(MIMEText(html_text, 'html', 'utf-8'))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    if user is not None:
        smtp.ehlo()
        if usessl is True:
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
        else:
            smtp_userid64 = base64.encodestring(user)
            smtp.docmd("auth", "login " + smtp_userid64[:-1])
            if password is not None:
                smtp_pass64 = base64.encodestring(password)
                smtp.docmd(smtp_pass64[:-1])

    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

if __name__ == "__main__":
    pass

