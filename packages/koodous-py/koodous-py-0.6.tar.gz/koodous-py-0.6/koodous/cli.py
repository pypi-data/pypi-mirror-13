#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015. The Koodous Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import glob
import io
import json
import logging
import os

import click

from koodous import Koodous
from utils import pygmentize_json, is_apk, sha256 as file_hash

__author__ = "Federico Maggi <federico.maggi@gmail.com>"

logger = logging.getLogger('koocli')

LOGGING_LEVELS = dict((
    ('notset', logging.NOTSET),
    ('debug', logging.DEBUG),
    ('info', logging.INFO),
    ('warning', logging.WARNING),
    ('error', logging.ERROR),
    ('critical', logging.CRITICAL),
))

loglevels = LOGGING_LEVELS.keys()


@click.group()
@click.option('--quiet/--no-quiet', default=False,
              help='Suppress output (logging is configured separately)')
@click.option('--wdir', type=click.Path(exists=False), required=True,
              help='Working directory')
@click.option('--loglevel', type=click.Choice(loglevels), default='info')
@click.option('--token', envvar='TOKEN', help='Koodous API token',
              required=True)
def cli(quiet, loglevel, wdir, token):
    """A simple command line interface (CLI) to the Koodous API.

    In order to use this CLI, you need an account at koodous.com and you
    need to grab your API token at https://koodous.com/settings/profile

    You can pass the API token both as a command line option, or set it as
    an environment variable (TOKEN).

    \b To get help for each individual command, just type

        $ koocli <command_name> --help

    """
    ctx = click.get_current_context()

    ctx.meta['TOKEN'] = token
    ctx.meta['api'] = Koodous(token=token)
    ctx.meta['wdir'] = wdir
    ctx.meta['quiet'] = quiet

    import coloredlogs
    coloredlogs.install(level=LOGGING_LEVELS[loglevel])


@cli.command()
@click.option('--save/--no-save', default=False,
              help='Save JSON to file in the working directory')
@click.option('--outfile', help='Optional file to save the metadata to',
              type=click.File('wb'))
@click.argument('ruleset_id', type=int)
def get_public_ruleset(save, outfile, ruleset_id):
    """Get a public ruleset by its RULESET_ID"""
    ctx = click.get_current_context()

    api = ctx.meta.get('api')
    wdir = ctx.meta.get('wdir')
    quiet = ctx.meta.get('quiet')

    logger.info('Attempting to fetch ruleset %s', ruleset_id)
    result = api.get_public_ruleset(ruleset_id=ruleset_id)

    if not quiet:
        click.echo(pygmentize_json(result))

    if save:
        if not outfile:
            filepath = os.path.join(wdir, 'ruleset-{}.json'.format(ruleset_id))
            outfile = io.open(filepath, 'wb')
        else:
            filepath = outfile.name
        logger.info('Saving ruleset metadata to {}'.format(filepath))

        json.dump(result, outfile)

        logger.info('Ruleset metadata saved correctly')


@cli.command()
@click.option('--save/--no-save', default=False,
              help='Save output as separate JSON files in the working '
                   'directory')
@click.option('--download/--no-download', default=False,
              help='Download the actual APK files and save them in the '
                   'working directory')
@click.option('--prompt/--no-prompt', default=True,
              help='Prompt for confirmations')
@click.option('--limit', type=int, default=0,
              help='Stop after LIMIT matches (defaults to 0, no limits)')
@click.argument('ruleset_id', type=int)
def get_matches_public_ruleset(ruleset_id, prompt, save, download, limit):
    """Get the APKs that match a public ruleset by its RULESET_ID

    Example: https://koodous.com/rulesets/RULESET_ID (e.g., 666)
    """
    ctx = click.get_current_context()

    api = ctx.meta.get('api')
    quiet = ctx.meta.get('quiet')
    wdir = ctx.meta.get('wdir')

    logger.info('Attempting to fetch ruleset %s', ruleset_id)
    ruleset = api.get_public_ruleset(ruleset_id=ruleset_id)

    d = ruleset['detections']

    if save:
        filepath = os.path.join(wdir, 'ruleset-{}.json'.format(
            ruleset_id))

        logger.info('Saving ruleset to %s', filepath)
        with io.open(filepath, 'wb') as outfile:
            json.dump(ruleset, outfile)

        logger.info('Ruleset saved successfully')

    if prompt and 100 < d <= limit:
        if not click.confirm('The selected ruleset has {} matches. Do you '
                             'want to proceed printing all of '
                             'them?'.format(d)):
            return

    iterator = api.iter_matches_public_ruleset(ruleset_id)
    count = 0

    for apks in iterator:
        for apk in apks:
            if not quiet:
                click.echo(pygmentize_json(apk))

            if save:
                sha256 = apk['sha256']

                filepath = os.path.join(wdir, '{}.json'.format(sha256))

                logger.info('Saving metadata of %s to %s', sha256, filepath)

                with io.open(filepath, 'wb') as outfile:
                    json.dump(apk, outfile)

            if download:
                dst = os.path.join(wdir, '{}.apk'.format(sha256))
                logger.info('Downloading %s to %s', sha256, dst)

                try:
                    api.download_to_file(sha256=sha256, dst=dst)
                    logger.info('APK downloaded successfully')
                except Exception as ex:
                    logger.error('Could not download %s: %s', sha256, ex)

            count += 1

            if 0 < limit <= count:
                logger.info('Limit of %s matches reached: stopping!', limit)
                return


@cli.command()
@click.argument('glob_exp')
@click.option('--ignore-bad-apks/--no-ignore-bad-apks',
              default=False, help='Bypass APK checks')
def upload(glob_exp, ignore_bad_apks):
    """Upload files matching the GLOB_EXP to Koodous.

    \b
    Example of GLOB_EXP are:
    \b
        - /path/to/*-files/*.apk
        - /path/*

    Some shell interpreters require you to wrap glob expression into
    single quotes to prevent automatic expansion:

        $ TOKEN='<your token>' koocli --wdir /tmp/ upload '/path/*.apk'

    Note that non-files will be obviously skipped. And we do try
    to skip non-APK files. Sometimes, however, malformed APKs exists that
    manage to bypass or fail the validation.
    """
    ctx = click.get_current_context()
    api = ctx.meta.get('api')
    quiet = ctx.meta.get('quiet')

    count = 0
    skipped = 0
    errors = 0

    for path in glob.glob(glob_exp):
        if os.path.isfile(path) and os.access(path, os.R_OK):
            if is_apk(path) or ignore_bad_apks:
                logger.info('Submitting file %s to Koodous', path)

                sha256 = None
                try:
                    sha256 = api.upload(path)
                except Exception as ex:
                    logger.error('Error uploading file %s: %s', path, ex)
                    errors += 1

                if sha256:
                    logger.info('File %s (%s) uploaded correctly', path,
                                sha256)

                    if not quiet:
                        click.echo(sha256)

                    count += 1
            else:
                logger.warning('Skipping file %s: invalid APK format', path)
                skipped += 1

    logger.info('Correctly submitted %d files (skipped %d, errors %d)',
                count, skipped, errors)


@cli.command()
@click.option('--upload/--no-upload', default=False,
              help='Upload the file for analysis if not found')
@click.option('--save/--no-save', default=False,
              help='Save JSON to file in the working directory')
@click.option('--outfile', help='Optional file to save the metadata to',
              type=click.File('wb'))
@click.argument('sha256_or_file')
def get_analysis(sha256_or_file, upload, save, outfile):
    """
    Get the Koodous report of SHA256_OR_FILE. If the file has not be analyzed
    by Koodous, the file is just submitted (or not, according to the
    --upload option).
    """
    ctx = click.get_current_context()
    api = ctx.meta.get('api')
    wdir = ctx.meta.get('wdir')

    is_file = os.path.isfile(sha256_or_file) and os.access(sha256_or_file,
                                                           os.R_OK)
    sha256 = sha256_or_file
    if is_file:
        sha256 = file_hash(sha256_or_file)
        logger.info('File %s SHA-256 digest = %s', sha256_or_file, sha256)

    logger.info('Getting analysis of %s', sha256)

    analysis = api.get_analysis(sha256)

    click.echo(analysis)

    if analysis:
        click.echo(pygmentize_json(analysis))

        if save:
            if not outfile:
                filepath = os.path.join(wdir, '{}.json'.format(sha256))
                outfile = io.open(filepath, 'wb')
            else:
                filepath = outfile.name

            logger.info('Saving analysis to %s', filepath)
            json.dump(analysis, outfile)

            logger.info('Saved to %s successfully', filepath)
    elif is_file:
        logger.warning('File not found on Koodous')

        if upload:
            logger.info('Uploading file for analysis')

            try:
                upload_result = api.upload(sha256_or_file)
                logger.info('File %s uploaded successfully', upload_result)
            except Exception as ex:
                logger.error('Uploading %s failed: %s', sha256_or_file, ex)
