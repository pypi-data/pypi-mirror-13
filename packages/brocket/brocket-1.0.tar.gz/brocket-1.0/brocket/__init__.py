# -*- coding: utf-8 -*-

from urlobject import URLObject


def is_amazon_url(url):
    amazon_url = URLObject(url)

    # Sanity checking, make sure we have an amazon URL.
    valid_hosts = ['amazon.com', 'www.amazon.com']

    if amazon_url.hostname not in valid_hosts:
        print("""The URL "{}" is not an Amazon URL.""".format(str(amazon_url)))
        return False

    return True


def process_url(url, tracking_id):
    amazon_url = URLObject(url)

    amazon_url = amazon_url.with_scheme('https')
    amazon_url = amazon_url.set_query_param('tag', tracking_id)

    return amazon_url
