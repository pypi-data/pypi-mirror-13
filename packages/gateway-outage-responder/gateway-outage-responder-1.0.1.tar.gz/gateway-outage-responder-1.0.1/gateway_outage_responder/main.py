import argparse
import logging
import subprocess
import time
import urllib2


logger = logging.getLogger(__name__)


def internet_is_accessible():
    try:
        urllib2.urlopen(
            'http://google.com',
            timeout=5
        )
        return True
    except urllib2.URLError:
        pass
    return False


def unplug_cable_modem():
    logger.debug('Turning off cable modem outlet...')
    subprocess.call([
        'stanley-outlet-control',
        '1',
        'off'
    ])


def plug_in_cable_modem():
    logger.debug('Turning on cable modem outlet...')
    subprocess.call([
        'stanley-outlet-control',
        '1',
        'on'
    ])


def unplug_router():
    logger.debug('Turning off router outlet...')
    subprocess.call([
        'stanley-outlet-control',
        '2',
        'off'
    ])


def plug_in_router():
    logger.debug('Turning on router outlet...')
    subprocess.call([
        'stanley-outlet-control',
        '2',
        'on'
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logfile')

    args = parser.parse_args()

    logging_kwargs = {
        'level': logging.DEBUG,
        'format': '%(asctime)s [%(levelname)s] %(message)s'
    }
    if args.logfile:
        logging_kwargs['filename'] = args.logfile

    logging.basicConfig(**logging_kwargs)

    if not internet_is_accessible():
        logger.warning('Internet appears to be offline.')
        unplug_cable_modem()
        unplug_router()

        plug_in_router()
        time.sleep(60)
        plug_in_cable_modem()
    else:
        logger.info('Internet appears to be accessible.')
