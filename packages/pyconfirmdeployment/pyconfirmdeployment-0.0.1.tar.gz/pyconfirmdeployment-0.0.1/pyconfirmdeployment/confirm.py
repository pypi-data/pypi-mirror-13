#!/usr/bin/env python
import os
from datetime import datetime

import sendgrid
from selenium import webdriver
from slugify import slugify


def set_file_name(url):
    # import ipdb; ipdb.set_trace()
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    return ''.join([
        slugify(url.decode('UTF-8')),
        '_',
        timestamp.decode('UTF-8'),
        '.png']
    )


def get_screenshot(url, file_name):
    browser = webdriver.Firefox()
    browser.maximize_window()
    browser.get(url)
    browser.save_screenshot(file_name)
    browser.quit()


def remove_screenshot(file_name):
    if os.path.isfile(file_name):
        os.remove(file_name)


def send_email_confirmation(url, file_name, to_emails, from_email):

    sg = sendgrid.SendGridClient(os.environ.get('SENDGRID_API_KEY', None))

    message = sendgrid.Mail()
    message.add_attachment(str(file_name), './' + str(file_name))
    for email in to_emails:
        message.add_to(email)
    message.set_subject('Deployment confirmation for {}'.format(url))
    message_text = (
        'Please find the deployment confirmation for {} attached to this email'
    ).format(url)
    message.set_html(message_text)
    message.set_text(message_text)
    message.set_from(from_email)
    status, msg = sg.send(message)


def get_confirmation(
        url,
        from_email='casey@example.com',
        to_emails=['lisa@example.com', ],
        ):

    file_name = set_file_name(url)
    get_screenshot(url, file_name)
    send_email_confirmation(url, file_name, to_emails, from_email)
    remove_screenshot(file_name)

if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(
        description=(
            'Checks webservers after a deployment and emails '
            'the given email addresses a screenshot')
        )
    parser.add_argument(
        '-u', '--url', help='URL to check',
        required=True)
    parser.add_argument(
        '-t', '--to', help='Receiving emails of the screenshot',
        required=True)
    parser.add_argument(
        '-f', '--fromemail', help='From email address',
        required=True)

    args = parser.parse_args()
    get_confirmation(
        args.url, to_emails=[args.to, ], from_email=args.fromemail,)
    print ('Deployment screenshot sent to {}').format(args.to)
