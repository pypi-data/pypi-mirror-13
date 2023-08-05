import argparse
import logging
import subprocess
import time
import urllib2


logger = logging.getLogger(__name__)


def url_is_accessible(url):
    try:
        urllib2.urlopen(url, timeout=5)
        return True
    except urllib2.URLError:
        pass
    return False


def unplug_cable_modem(binpath):
    logger.debug('Turning off cable modem outlet...')
    subprocess.call([
        binpath,
        '1',
        'off'
    ])


def plug_in_cable_modem(binpath):
    logger.debug('Turning on cable modem outlet...')
    subprocess.call([
        binpath,
        '1',
        'on'
    ])


def unplug_router(binpath):
    logger.debug('Turning off router outlet...')
    subprocess.call([
        binpath,
        '2',
        'off'
    ])


def plug_in_router(binpath):
    logger.debug('Turning on router outlet...')
    subprocess.call([
        binpath,
        '2',
        'on'
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile')
    parser.add_argument('--url', default='http://google.com')
    parser.add_argument('--stanley-path', default='stanley-outlet-control')

    args = parser.parse_args()

    logging_kwargs = {
        'level': logging.DEBUG,
        'format': '%(asctime)s [%(levelname)s] %(message)s'
    }
    if args.logfile:
        logging_kwargs['filename'] = args.logfile

    logging.basicConfig(**logging_kwargs)

    if not url_is_accessible(args.url):
        logger.warning('Internet appears to be offline.')
        unplug_cable_modem(args.stanley_path)
        unplug_router(args.stanley_path)

        plug_in_router(args.stanley_path)
        time.sleep(60)
        plug_in_cable_modem(args.stanley_path)
    else:
        logger.info('Internet appears to be accessible.')
