#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import with_statement

import pkg_resources
from pkg_resources import resource_filename
import argparse
import sys
import requests
import feedparser
import re
from pprint import pformat
from pathlib import Path
from bs4 import BeautifulSoup
import yaml
import logging
try:
    from urllib.parse import urljoin # py3
except:
    from urlparse import urljoin # py2


def _create_logger(logfile_path, verbose):
    format_ = '[%(asctime)s]%(levelname)7s:%(filename)s:%(lineno)d: %(message)s'
    formatter = logging.Formatter(format_)

    log_level = logging.DEBUG if verbose else logging.INFO

    logger_ = logging.getLogger()
    logger_.setLevel(log_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger_.addHandler(console_handler)

    if logfile_path:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=logfile_path,
            maxBytes=1 * 1024 * 1024,
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger_.addHandler(file_handler)

    return logger_


def _get_created_repositories(feed_url):
    created_repositories = []
    feed = feedparser.parse(feed_url)
    regex = re.compile(r'<a href=.*</a> (?P<activity>[a-zA-Z]+) <a href=.*</a>')
    created_repositories = []
    for entry in feed['entries'] :
        content = entry['content'][0]
        match = regex.match(content['value'])
        if match:
            activity = match.group('activity')
            if activity == 'created':
                created_repositories.append(entry['link'])

    return created_repositories


def _login(url, user, password):
    session = requests.session()
    login_data = {
        'userName': user,
        'password': password,
    }
    res = session.post(url, data=login_data)
    res.raise_for_status()

    return session


def _get_existing_service_hooks(session, url):
    existing_service_hooks = []
    res = session.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    selector = 'body > div.wrapper > div.content-wrapper > div > div.panel.panel-default > div.panel-body > table'
    table = soup.select(selector)[0]
    rows = table.findAll('tr')
    existing_service_hooks = []
    for i, r in enumerate(rows):
        selector = 'td:nth-child(1) > a > span'
        v = r.select(selector)[0]
        existing_service_hooks.append(v.get_text())

    return existing_service_hooks


def _inject_service_hook(session, url, service_hook):
    events = service_hook['events']
    service_hook_data = {
        'url': service_hook['url'],
        'ctype': service_hook.get('ctype', 'json'),
        'token': service_hook.get('token', ''),
    }
    for k, v in events.items():
        if v:
            service_hook_data['events.' + k] = 'on'
    res = session.post(url, data=service_hook_data)
    res.raise_for_status()


def main():
    argparser = argparse.ArgumentParser(
        description='Set up a service hook in the GitBucket repository',
        epilog='See more details: https://github.com/maskedw/gitbucket-servicehook-injector',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    try:
        version = pkg_resources.require('gitbucket-servicehook-injector')[0].version
    except:
        version = '?.?.?'

    argparser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(version))
    argparser.add_argument(
        '--log',
        required=False,
        default='',
        help='Log file path')
    argparser.add_argument(
        "--beacon",
        required=False,
        default=False,
        action='store_true',
        help='Prints a message at startup')
    argparser.add_argument(
        '-v', '--verbose',
        required=False,
        default=False,
        action='store_true',
        help="Enable verbose output")
    argparser.add_argument(
        "config_file",
        help="Configuration File(YAML)")

    args = argparser.parse_args()

    logger = _create_logger(args.log, args.verbose)
    logger.debug('args =\n{}'.format(pformat(args)))

    if args.beacon:
        logger.info('start app')

    try:
        with open(args.config_file) as f:
            cfg = yaml.safe_load(f)
        logger.debug('cfg =\n{}'.format(pformat(cfg)))

        created_repositories = _get_created_repositories(cfg['feed_url'])
        logger.debug('created_repositories =\n{}'.format(
            pformat(created_repositories)))

        if created_repositories:
            session = _login(
                urljoin(cfg['root_url'] + '/', 'signin'),
                cfg['admin_user']['name'],
                cfg['admin_user']['password'])

            for repo in created_repositories:
                existing_service_hooks = _get_existing_service_hooks(
                    session,
                    urljoin(repo + '/', 'settings/hooks'))

                logger.debug('"{}" existing_service_hooks =\n{}'.format(
                    repo,
                    pformat(existing_service_hooks)))


                for hook in cfg['service_hooks']:
                    hook_url = hook['url']
                    if hook_url in existing_service_hooks:
                        logger.debug('"{}" already exists'.format(hook_url))
                        continue

                    _inject_service_hook(
                        session,
                        urljoin(repo + '/', 'settings/hooks/new'),
                        hook)
                    logger.info('"{}" add service hook: "{}"'.format(
                        repo, hook_url))
    except Exception as e:
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
