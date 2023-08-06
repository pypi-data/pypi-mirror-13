#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import json
import logging
import re
import signal
import tempfile
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path

import click
import requests
from dirq.QueueSimple import QueueSimple

from bottle import Bottle, request, run

######################################################################
# Globals
######################################################################

HERE = Path(__file__).parent

######################################################################
# `scoutSubmit.asp` extension with attachments
######################################################################


def dump_error(errors_path, parts):
    with tempfile.NamedTemporaryFile(mode='w+',
                                     prefix='err',
                                     suffix='.foz',
                                     delete=False,
                                     dir=str(errors_path)) as dump:
        pdump = Path(dump.name)
        ddump = pdump.with_name(pdump.stem)
        files = []
        if parts['files']:
            ddump.mkdir()
            for file in parts['files']:
                attachment = ddump / file.filename
                with attachment.open('w+b') as f:
                    file.save(f)
                files.append(str(attachment.relative_to(errors_path.resolve())))
        json.dump({'forms': parts['forms'], 'files': files}, dump)
    return dump.name, parts['forms']['sScoutDescription']


def prepare_dump(request):
    forms = dict(request.forms)
    forms.pop(None, None)
    forms['sScoutDescription'] = re.sub('\d{4,}', '<DIGITS>', forms['Description'])
    files = request.files.values()
    return {'forms': forms, 'files': files}


def get_scout_message(messages_path, scout_desc):
    message = scout_desc.encode('utf8')
    message_hash = hashlib.md5(message).hexdigest()
    message_cache = (messages_path / message_hash).with_suffix('.message')
    if message_cache.exists():
        return message_cache.read_text('utf8')
    else:
        return None


def bottle_app(errors_path, messages_path):
    app = Bottle()
    errors_queue = QueueSimple(str(errors_path / 'queue'))

    @app.route('/scoutSubmit.asp', method='POST')
    def save_report():
        name, scout_desc = dump_error(errors_path, prepare_dump(request))
        message = get_scout_message(messages_path, scout_desc)
        content = ET.Element("Success")
        if message is not None:
            content.text = message
        # enqueue error for upload
        errors_queue.add(name)
        return ET.tostring(content, encoding='utf8')

    return app

######################################################################
# Use full fogbugz api to push the reported error and save the message
######################################################################


def load_error(errors_path, name):
    with open(name) as f:
        parms = json.loads(f.read())
    forms = parms['forms']
    files = [Path(errors_path / filename) for filename in parms['files']]
    return forms, files


def prepare_request(errors_path, api, token, name):
    forms, files = load_error(errors_path, name)
    data = {'token': token,
            'cmd': 'new',
            'sScoutDescription': forms['sScoutDescription'],
            'sTitle': forms['Description'],
            'sEvent': forms['Extra']}
    files = {'File%d' % (c + 1): (file.name, BytesIO(file.read_bytes()))
             for c, file in enumerate(files)}
    if len(files) > 1:
        data['nFileCount'] = len(files)
    return data, files


def push_error(errors_path, messages_path, api, token, name):
    data, files = prepare_request(errors_path, api, token, name)
    r = requests.post(api, data=data, files=files)
    if r.status_code == requests.codes.ok:
        cache_scout_message(messages_path, api, token, data['sScoutDescription'])


def cache_scout_message(messages_path, api, token, scout_desc):
    params = {'token': token, 'cmd': 'listScoutCase', 'sScoutDescription': scout_desc}
    r = requests.get(api, params=params)
    if r.status_code == requests.codes.ok:
        response = ET.XML(r.content)
        message_tag = response.find('*sScoutMessage')
        if message_tag is not None and message_tag.text is not None:
            message = scout_desc.encode('utf8')
            message_hash = hashlib.md5(message).hexdigest()
            message_cache = messages_path / message_hash
            if not message_cache.with_suffix('.message').exists():
                message_cache.write_text(message_tag.text, encoding='utf8')
                message_cache.rename(message_cache.with_suffix('.message'))


def consume_errors(errors_path, messages_path, api, token, log):
    log.debug("Consuming queue...")
    errors_queue = QueueSimple(str(errors_path / 'queue'))
    for item in errors_queue:
        if not errors_queue.lock(item):
            continue
        try:
            name = errors_queue.get(item)
            log.debug("Pushing error %r", name)
            push_error(errors_path, messages_path, api, token, name)
            errors_queue.remove(item)
        except:
            errors_queue.unlock(name)
            log.exception("Error uploading error %r", name)
    log.debug("Queue consumed!")

######################################################################
# Utils
######################################################################


def create_folders(spool_dir):
    errors = spool_dir / 'errors'
    if not errors.exists():
        errors.mkdir()
    messages = spool_dir / 'messages'
    if not messages.exists():
        messages.mkdir()
    return {'errors': errors, 'messages': messages}


def setup_logging(level):
    logger = logging.getLogger('fogproxy')
    logger.setLevel(level)

    # Do not propagate logging messages
    logger.propagate = False

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

######################################################################
# Command line
######################################################################


@click.group()
@click.option('--spool-dir',
              default=str(HERE),
              type=click.Path(writable=True),
              help='Data folder (default: executable folder)')
@click.pass_context
def cli(ctx, spool_dir):
    ctx.obj['spool_dir'] = spool_dir = Path(spool_dir)
    ctx.obj.update(**create_folders(spool_dir))


@cli.command()
@click.argument('apiurl')
@click.argument('token')
@click.option('--loop/--no-loop', default=False, help='Loop and consume queue on SIGHUP')
@click.pass_context
def uploader(ctx, apiurl, token, loop):
    log = logging.getLogger('fogproxy.ScoutUploader')
    log.info("Starting uploader...")

    def _consume_errors(*args):
        errors_path = ctx.obj['errors']
        messages_path = ctx.obj['messages']
        consume_errors(errors_path, messages_path, apiurl, token, log)

    signal.signal(signal.SIGHUP, _consume_errors)

    def gracefull_term(*args):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, gracefull_term)

    try:
        _consume_errors()
        while loop:
            signal.pause()
    except (KeyboardInterrupt, SystemError):
        pass

    log.info("Exiting from uploader!")


@cli.command()
@click.option('--host', default='localhost', help='Serve on provided host')
@click.option('--port', default=8000, help='Use provided port')
@click.pass_context
def proxy(ctx, host, port):
    errors_path = ctx.obj['errors']
    messages_path = ctx.obj['messages']
    log = logging.getLogger('fogproxy.ScoutProxy')
    log.info("Starting proxy...")
    # bottle gracefully handles a KeyboardInterrupt exception
    app = bottle_app(errors_path, messages_path)
    run(app=app, host=host, port=port, debug=__debug__)
    log.info("Exiting from proxy!")


if __name__ == '__main__':
    setup_logging(logging.DEBUG)
    cli(obj={})
