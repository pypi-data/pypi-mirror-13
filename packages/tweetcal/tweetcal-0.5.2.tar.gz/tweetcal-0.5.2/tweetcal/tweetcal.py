#!/usr/bin/env python
# encoding: utf-8
# Tweetcal: Convert a tweet stream to ics calendar
# Copyright (c) 2014-2015 Neil Freeman
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from __future__ import unicode_literals, print_function
from os import path
from datetime import timedelta
import logging
try:
    from HTMLParser import HTMLParser
    html = HTMLParser()
except ImportError:
    import html
import pytz
from icalendar import Calendar, Event
import twitter_bot_utils as tbu
import tweepy


def setup_logger(verbose=None):
    logger = logging.getLogger('tweetcal')

    if verbose:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('tweetcal: %(message)s'))
        logger.addHandler(ch)

    return logger


def get_settings(screen_name, config, **kwargs):
    '''Get settings and OAuth keys based on passed Namespace of args
    - screen_name (string)
    - config (file path)
    - verbose (boolean)
    - dry_run (boolean)
    '''
    setup_logger(kwargs.get('verbose') or kwargs.get('dry_run'))

    settings = tbu.confighelper.configure(screen_name, app='tweetcal', file_name=config, **kwargs)

    settings['screen_name'] = screen_name
    settings['limit'] = max(kwargs.get('max', 100), 1)

    return settings


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=1)
    return start, end


def create_event(tweet):
    event = Event()

    try:
        # Add link to tweet.
        try:
            url = 'http://twitter.com/{0}/status/{1}'.format(tweet.user.screen_name, tweet.id_str)
        except AttributeError:
            url = 'http://twitter.com/{0}/status/{1}'.format(tweet.screen_name, tweet.id_str)

        event.add('url', url)

        # Add tweet's text.
        text = tbu.helpers.replace_urls(tweet)
        text = html.unescape(text)
        event.add('summary', text)

        # Add tweet's date.
        dtstart, dtend = parse_date(tweet.created_at)
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)

        # Add UID and special field for ID.
        try:
            event.add('uid', '{0}@{1}.twitter'.format(tweet.id_str, tweet.user.screen_name))
        except AttributeError:
            event.add('uid', '{0}@{1}.twitter'.format(tweet.id_str, 'archive'))

        event['X-TWEET-ID'] = tweet.id_str

    except Exception as e:
        logger = logging.getLogger('tweetcal')
        logger.error(e)
        logger.error("{0} [{1} created at {2}]".format(tweet.text, tweet.id_str, tweet.created_at))

    else:
        return event


def get_calendar(filename):
    '''Open calendar file and return as Calendar object, along with list of IDs retrieved (to avoid dupes)'''
    expanded = path.expanduser(filename)

    with open(expanded, 'rb') as h:
        contents = h.read()
        logging.getLogger('tweetcal').info("Opened calendar file " + filename)

    if len(contents) == 0:
        raise IOError("Empty Calendar")

    return Calendar.from_ical(contents)


def new_calendar(screen_name=None):
    logging.getLogger('tweetcal').info("Creating new calendar.")
    if screen_name:
        name = screen_name + ' tweets'
    else:
        name = 'Tweets'

    cal = Calendar()
    cal.add('PRODID', '-//tweetcal//twitter importer//EN')
    cal.add('X-WR-CALNAME', name)
    return cal


def get_since_id(cal, since_id=None):
    '''Set the max and since ids to request from twitter. If the calendar has a max ID, use it as the since'''

    since_id = (
        since_id or cal.get('X-MAX-TWEET-ID') or
        max(int(x.get('X-TWEET-ID') or 0) for x in cal.subcomponents + [{'X-TWEET-ID': 0}]) or None
    )

    logging.getLogger('tweetcal').debug('Setting since_id: {}'.format(since_id))

    if since_id:
        return {
            'since_id': str(since_id)
        }
    else:
        return {}


def set_max_id(cal, ids):
    '''Combine set of read IDs and just-added IDs to get the new max id'''
    try:
        max_id = max(ids)

    # If that's empty, there will be a ValueError, which is fine.
    except ValueError:
        max_id = 0

    cal['X-MAX-TWEET-ID'] = max(cal.get('X-MAX-TWEET-ID', 100000), max_id)

    logging.getLogger('tweetcal').debug('Set {1} to {0}'.format(max_id, 'X-MAX-TWEET-ID'))


def set_color(cal, status):
    if hasattr(status, 'screen_name') and hasattr(status.user, 'profile_link_color'):
        cal['X-APPLE-CALENDAR-COLOR'] = '#' + status.user.profile_link_color


def get_tweets(consumer_key, consumer_secret, key, secret, **kwargs):
    # Auth and check twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)

    logging.getLogger('tweetcal').debug(
        "Setting up connection to Twitter API (since_id: {})".format(kwargs.get('since_id')))

    return tweepy.Cursor(api.user_timeline, **kwargs)


def add_to_calendar(cal, generator, limit=None):
    """Add tweets to the calendar object"""
    ids, status = (), None

    # Loop the cursors and create the events if the tweet doesn't yet exist

    for status in generator(limit):
        event = create_event(status)
        cal.add_component(event)

        try:
            ids = ids + (status.id, )
        except AttributeError:
            ids = ids + (int(status.id_str), )

    logging.getLogger('tweetcal').info('Inserted {} tweets.'.format(len(ids)))

    set_color(cal, status)
    set_max_id(cal, ids)


def write_calendar(cal, calendar_file):
    filepath = path.expanduser(calendar_file)
    logging.getLogger('tweetcal').info('Saving to {}.'.format(filepath))

    with open(filepath, 'wb') as fh:
        fh.write(cal.to_ical())


def tweetcal(screen_name, config, **kwargs):
    logger = logging.getLogger('tweetcal')

    try:
        settings = get_settings(screen_name, config, **kwargs)

    except IOError as e:
        print(e)
        exit()

    try:
        cal = get_calendar(settings['file'])

    except IOError as e:
        logger.info("Didn't find %s, got error: %s", settings['file'], e)
        cal = new_calendar(settings['screen_name'])

    logger.info('since: %s', settings.get('since_id'))

    since = get_since_id(cal, settings.get('since_id'))

    cursor = get_tweets(
        consumer_key=settings['consumer_key'],
        consumer_secret=settings['consumer_secret'],
        key=settings['key'],
        secret=settings['secret'],
        **since
    )

    logger.info("Grabbing tweets for @" + settings['screen_name'])

    try:
        add_to_calendar(cal, cursor.items, limit=settings['limit'])

    except tweepy.error.TweepError as e:
        print(e.message)
        exit(-1)

    if settings['dry_run']:
        logger.info('Ending without rewriting file.')

    else:
        logger.info('Writing tweets to file.')
        write_calendar(cal, settings['file'])
