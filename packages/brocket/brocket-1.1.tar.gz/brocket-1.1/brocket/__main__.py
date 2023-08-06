import os
import sys
import argparse
import configparser

import pyperclip
from pync import Notifier

import brocket

prefs_file = os.path.expanduser("~/.brocket.cfg")

parser = argparse.ArgumentParser(
    description='Make an Amazon link and Amazon Associates link.'
)

parser.add_argument(
    '--url',
    dest='amazon_url',
    default=None,
    help='An Amazon URL (default: whatever is on the clipboard).'
)

parser.add_argument(
    '--tracking-id',
    dest='tracking_id',
    default=None,
    help='The tracking-id to use (default: saved tracking-id in settings).'
)

parser.add_argument(
    '--show-tracking-id',
    dest='show_tracking_id',
    action='store_true',
    default=False,
    help='Print out the saved Amazon Associates tracking-id.'
)

parser.add_argument(
    '--set-tracking-id',
    dest='set_tracking_id',
    default=None,
    help='Set the tracking-id in the settings.'
)


def save_tracking_id(tracking_id):
    config = configparser.ConfigParser()
    config['brocket'] = {}
    config['brocket']['tracking_id'] = tracking_id
    with open(prefs_file, 'w') as configfile:
        config.write(configfile)


def load_tracking_id():
    config = configparser.ConfigParser()
    config.read(prefs_file)
    return config['brocket']['tracking_id']


def main():
    args = parser.parse_args()

    # Setup the default config file if it's not there.
    if not os.path.isfile(prefs_file):
        tracking_id = input('Enter Amazon Associates Tracking ID: ')
        save_tracking_id(tracking_id)
        sys.exit(0)

    if args.show_tracking_id:
        print(load_tracking_id())
        sys.exit(0)

    if args.set_tracking_id:
        save_tracking_id(args.set_tracking_id)
        print("Tracking ID updated: {}".format(args.set_tracking_id))
        sys.exit(0)

    if args.tracking_id is None:
        tracking_id = load_tracking_id()
    else:
        tracking_id = args.tracking_id

    via_clipboard = False

    if args.amazon_url is None:
        url = pyperclip.paste()
        via_clipboard = True
    else:
        url = args.amazon_url

    if not brocket.is_amazon_url(url):

        Notifier.notify(
            'Not an Amazon URL on the clipboard.',
            title='Brocket Error',
            group="name.rupe.jachin.brocket"
        )

        sys.exit(1)

    amazon_assocate_url = brocket.process_url(url, tracking_id)

    if via_clipboard:
        msg = (
            "Adding the tracking {} to the URL {} and putting it on the"
            " clipboard."
        )

        print(msg.format(tracking_id, url))

        pyperclip.copy(amazon_assocate_url)

        Notifier.notify(
            'Amazon URL Saved to Clipboard',
            title='Brocket Success',
            group="name.rupe.jachin.brocket",
            open=url
        )

    print(amazon_assocate_url)

if __name__ == "__main__":
    main()
