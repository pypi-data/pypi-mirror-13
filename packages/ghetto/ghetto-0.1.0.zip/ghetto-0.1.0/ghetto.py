#/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import shutil
import requests
import json
from argparse import ArgumentParser, HelpFormatter
from subprocess import call
from lxml import etree
from crontab import CronTab


VERSION="0.1.0"
DESCRIPTION = """
A tool for (automatized) torrent files downloading from RSS feeds to use
with torrent clients which don't have built-in RSS functionality.
Supports multiple configurations, update crontab by itself to grab feeds
automatically.
"""

CONFIG_ROOT = os.path.join(os.path.expanduser('~'), '.config/ghetto')
DEFAULT_TORRRENT_DIR = os.path.join(os.path.expanduser('~'), 'torrent')
DEFAULT_UPDATE_INTERVAL = 10


def confirm(text, default=True):
    """
    Console confirmation dialog based on raw_input.
    """
    if default:
        legend = "[y]/n"
    else:
        legend = "y/[n]"
    res = ""
    while (res != "y") and (res != "n"):
        res = raw_input(text + " ({}): ".format(legend)).lower()
        if not res and default:
            res = "y"
        elif not res and not default:
            res = "n"
    if res[0] == "y":
        return True
    else:
        return False


def ensure_dir(d):
    """
    Check does directory exist, and create an empty one if not.
    """
    if not os.path.exists(d):
        os.makedirs(d)


def read_file(fname):
    """
    Read file, convert wildcards into regular expressions, skip empty lines
    and comments.
    """
    res = []
    try:
        with open(fname, 'r') as f:
            for line in f:
                line = line.rstrip('\n').rstrip('\r')
                if line and (line[0] != '#'):
                    regexline = ".*" + re.sub("\*", ".*", line) + ".*"
                    res.append(regexline.lower())
    except IOError:
        pass
    return res


def drop_it(title, filters, blacklist):
    """
    The found torrents should be in filters list and shouldn't be in blacklist.
    """
    title = title.lower()
    matched = False
    for f in filters:
        if re.match(f, title):
            matched = True
    if not matched:
        return True
    for b in blacklist:
        if re.match(b, title):
            return True
    return False


def do_list():
    """
    CLI action "list configurations".
    """
    dirs =  os.walk(CONFIG_ROOT).next()[1]
    if dirs:
        print "List of available configurations:\n"
        for d in dirs:
            print "  * {}".format(d)
    else:
        print "No configurations available."


def do_create(config, config_dir):
    """
    CLI action "create new configuration".
    """
    if os.path.exists(config_dir):
        print "Configuration '{}' already exists.".format(config)
        exit(1)
    os.makedirs(config_dir)
    print "Configuration directory created."

    url = raw_input("RSS URL for processing []: ")
    torrent_dir = raw_input("Output directory for found .torrent files [{}]: "\
        .format(DEFAULT_TORRRENT_DIR)) or DEFAULT_TORRRENT_DIR
    update_interval = raw_input("Update interval (mins) [{}]: "\
        .format(DEFAULT_UPDATE_INTERVAL)) or DEFAULT_UPDATE_INTERVAL

    editor = os.environ["EDITOR"]

    config_filter = os.path.join(config_dir, 'filter')
    if confirm("Do you want to create filters list?", False):
        call([editor, config_filter])
        print "Filter configuration has been saved."

    config_blacklist = os.path.join(config_dir, 'blacklist')
    if confirm("Do you want to create blacklist?", False):
        call([editor, config_filter])
        print "Blacklist configuration has been saved."

    config_file = os.path.join(config_dir, 'config')
    config_data = json.dumps({
        "url": url,
        "torrent_dir": torrent_dir,
        "update_interval": update_interval
    }, sort_keys=True, indent=4, separators=(',', ': '))
    with open(config_file, 'w') as f:
        f.write(config_data)

    ct = CronTab(user=True)
    cmd = "{} {} -e {}".format(sys.executable,
                               os.path.abspath(__file__),
                               config)
    job = ct.new(command=cmd)
    job.minute.every(update_interval)
    job.enable()
    ct.write()
    print "Crontab updated."

    print "Config '{}' has been saved.".format(config)


def do_update(config, config_dir):
    """
    CLI action "update new configuration".
    """
    if not os.path.exists(config_dir):
        print "Configuration '{}' does not exist.".format(config)
        exit(1)

    config_file = os.path.join(config_dir, 'config')
    with open(config_file, 'r') as f:
        old_config_data = json.load(f)

    old_url = old_config_data['url']
    old_torrent_dir = old_config_data['torrent_dir']
    old_update_interval = old_config_data['update_interval']

    url = raw_input("RSS URL for processing [{}]: "\
        .format(old_url)) or old_url
    torrent_dir = raw_input("Output directory for found .torrent files [{}]: "\
        .format(old_torrent_dir)) or old_torrent_dir
    update_interval = raw_input("Update interval (mins) [{}]: "\
        .format(old_update_interval)) or old_update_interval

    editor = os.environ["EDITOR"]

    config_filter = os.path.join(config_dir, 'filter')
    if confirm("Do you want to edit filters list?", False):
        call([editor, config_filter])
        print "Filter configuration has been saved."

    config_blacklist = os.path.join(config_dir, 'blacklist')
    if confirm("Do you want to edit blacklist?", False):
        call([editor, config_filter])
        print "Blacklist configuration has been saved."

    config_data = json.dumps({
        "url": url,
        "torrent_dir": torrent_dir,
        "update_interval": update_interval
    }, sort_keys=True, indent=4, separators=(',', ': '))
    with open(config_file, 'w') as f:
        f.write(config_data)

    ct = CronTab(user=True)
    for job in ct:
        if re.match('.*ghetto.*\-e\s{}'.format(config), job.command):
            ct.remove(job)

    cmd = "{} {} -e {}".format(sys.executable,
                               os.path.abspath(__file__),
                               config)
    new_job = ct.new(command=cmd)
    new_job.minute.every(update_interval)
    new_job.enable()
    ct.write()
    print "Crontab updated."

    print "Configuration '{}' has been updated.".format(config)


def do_remove(config, config_dir):
    """
    CLI action "remove configuration".
    """
    if not os.path.exists(config_dir):
        print "Configuration '{}' does not exist.".format(config)
        exit(1)
    if confirm("Confirm removal of the configuration '{}'".format(config)):
        shutil.rmtree(config_dir)
        print "Configuration '{}' has been removed.".format(config)
    else:
        print "Removal cancelled."


def do_exec(config, config_dir):
    """
    CLI action "process the feed from specified configuration".
    """
    if not os.path.exists(config_dir):
        print "Configuration '{}' does not exist.".format(config)
        exit(1)

    print "The parser for '{}' config has been initialized.".format(config)

    config_file = os.path.join(config_dir, 'config')
    with open(config_file, 'r') as f:
        config_data = json.load(f)

    url = config_data['url']
    torrent_dir = config_data['torrent_dir']
    ensure_dir(torrent_dir)

    filters_file = os.path.join(config_dir, 'filter')
    filters = read_file(filters_file)

    blacklist_file = os.path.join(config_dir, 'blacklist')
    blacklist = read_file(blacklist_file)

    print "Fetching URL {}".format(url)
    r = requests.get(url)
    if r.status_code != 200:
        print "Failed to fetch RSS feed."

    xml = r.text.encode('utf-8')
    parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
    tree  = etree.fromstring(xml, parser)
    items = tree.xpath('//item')
    downloaded = 0
    for e in items:
        e_title = e.xpath('title')[0].text
        e_link = e.xpath('link')[0].text
        if not drop_it(e_title, filters, blacklist):
            downloaded += 1
            target_file = os.path.join(torrent_dir, e_title + '.torrent')
            r = requests.get(e_link, stream=True)
            with open(target_file, 'wb') as f:
                for chunk in r.iter_content(4096):
                    f.write(chunk)

    print "Items found: {}, items downloaded: {}."\
        .format(len(items), downloaded)


def do_filter(config, config_dir):
    """
    CLI action "run editor for filters list".
    """
    if not os.path.exists(config_dir):
        print "Configuration '{}' does not exist.".format(config)
        exit(1)    

    editor = os.environ["EDITOR"]

    config_filter = os.path.join(config_dir, 'filter')
    call([editor, config_filter])
    print "Filter configuration has been updated."


def do_blacklist(config, config_dir):
    """
    CLI action "run editor for blacklist".
    """
    if not os.path.exists(config_dir):
        print "Configuration '{}' does not exist.".format(config)
        exit(1)    

    editor = os.environ["EDITOR"]

    config_blacklist = os.path.join(config_dir, 'blacklist')
    call([editor, config_blacklist])
    print "Blacklist configuration has been updated."


def action(act, config):
    """
    CLI action preprocessor
    """
    if not config:
        pass
    elif act is "list":
        do_list()
    else:
        config_dir = os.path.join(CONFIG_ROOT, config)
        globals()["do_" + act](config, config_dir)


def main():
    ensure_dir(CONFIG_ROOT)

    parser = ArgumentParser(version="%(prog)s {}".format(VERSION),
                            description=DESCRIPTION,
                            formatter_class=lambda prog:
                                HelpFormatter(prog,max_help_position=50))
    parser.add_argument("-l", "--list", action="store_true",
                        help="list of available configs")
    parser.add_argument("-c", "--create", metavar="CONFIG",
                        help="create a new config")
    parser.add_argument("-u", "--update", metavar="CONFIG",
                        help="update an existent config")
    parser.add_argument("-r", "--remove", metavar="CONFIG",
                        help="remove the config")
    parser.add_argument("-e", "--exec", metavar="CONFIG",
                        help="run parser with the specified config")
    parser.add_argument("-f", "--filter", metavar="CONFIG",
                        help="edit filters list for the specified config")
    parser.add_argument("-b", "--blacklist", metavar="CONFIG",
                        help="edit blacklist for the specified config")
    
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)

    args = vars(parser.parse_args())
    [globals()["action"](key, arg) for key, arg in args.iteritems()]


if __name__ == "__main__":
    main()
