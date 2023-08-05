#!/usr/bin/python3
import os
import sys
import argparse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

conf_path = "/etc/gymail.conf"
conf = {}

try:
    with open(conf_path) as f:
        code = compile(f.read(), conf_path, 'exec')
        exec(code, conf)
    (sender, recipient, username, password,
     smtp_address) = (conf.get("sender", None), conf.get("recipient", None), conf.get("username", None),
                      conf.get("password", None), conf.get("smtp", None))
except Exception as err:
    print("(E) Missing {0}. {1}".format(conf_path, err))
    sys.exit(0)


def send_mail(event, subject, message, sender=sender, recipient=recipient, username=username, password=password, smtp_address=smtp_address):
    if not sender and recipient and username and password and smtp_address:
        raise ValueError("Missing setting/parameter.")
    msg = MIMEMultipart('alternative')  # (1)
    msg['sender'] = sender
    msg['recipient'] = recipient
    style = '<style type="text/css">body {{ background-color: {0};}} p {{ color: black; font-size: 28px;}}</style>'  # (2)
    error_style = style.format('red')
    warning_style = style.format('yellow')
    info_style = style.format('green')
    template = "<html>{0}<body><p>{1}</p></body></html>"
    if event == "error":
        html = template.format(error_style, message)
        msg['Subject'] = "error: " + subject
    elif event == "warning":
        html = template.format(warning_style, message)
        msg['Subject'] = "warning: " + subject
    elif event == "info":
        html = template.format(info_style, message)
        msg['Subject'] = "info: " + subject
    part1 = MIMEText(message, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)
    s = smtplib.SMTP(smtp_address)
    s.starttls()
    s.login(username, password)
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()


def argparse_entrypoint():
    parser = argparse.ArgumentParser(description='Simple sendmail script.')
    parser.add_argument('-e', '--event', choices=['error', 'warning', 'info'], help='Formats html style for email accordingly.', required=True)
    parser.add_argument('-s', '--subject', help='Subject of email.', required=True)
    parser.add_argument('-m', '--msg', help='Email message goes here.', required=True)
    args = parser.parse_args()
    send_mail(args.event, args.subject, args.msg)


# Description:
# gymail can be either used as module or cli script. if no sender, recipient, username, password or smtp_address
# were provided, then gymail looks in /etc/gymail.conf for the settings.
#
# Configuration exmaple /etc/gymail.conf:
#
#   username = 'your_username'
#   password = 'your_email_password'
#   sender = 'sender@gmail.com'
#   recipient = 'recipient@gmail.com'
#   smtp = 'smtp.gmail.com:587'
#
# Code notes:
# (1) Create message container; the correct MIME type is multipart/alternative.
# (2) Escaping with double curly brackets. Alternatively switch to old %s style.
