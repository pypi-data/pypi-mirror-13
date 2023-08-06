#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mchallenge_me` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``challenge_me.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``challenge_me.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import click

from . import challenge_me, __version__


@click.group()
@click.version_option(prog_name="challenge-me", version=__version__)
def main():
    """
    Command line tool for running programming challenges.

    This is still an early version which can have
    unwanted side effects like accidentally deleting a wrong file. Use with care.
    """
    pass


@main.command()
@click.argument('category', required=False)
@click.option('--language', default="python", required=False,
              help="The programming language that the file should be created in.")
def start(category, language):
    """
    Starting a challenge.

    Args:
        language:
        category:
    """

    try:
        if category:
            number = challenge_me.current_attempt_in_category(category)
        else:
            category, number = challenge_me.current_attempt()

        if not category:
            click.echo("Couldn't find a category with open challenges. Stopping.")
            return
        elif number != 1:
            click.echo("The category {} already exists. Skipping creating it.".format(category))
            return

        # TODO: choose first challenge with tests
        challenge = challenge_me.get_challenge(category, number)

        click.echo('Starting first challenge for category {}.'.format(category))
        challenge_me.create_attempt(challenge, language)
    except ValueError as e:
        click.echo(str(e) + " Stopping.")


@main.command()
@click.argument('category', required=False)
@click.argument('number', type=int, required=False)
@click.option('--language', default="python", required=False)
def verify(category, number, language):
    """
    Verifying a challenge.

    Args:
        language:
        number:
        category:
    """
    try:
        current_category = category
        if category and not number:
            number = challenge_me.current_attempt_in_category(category)
        elif not category and not number:
            current_category, number = challenge_me.current_attempt()

        if category and category != current_category:
            click.echo("Already verified all attempts in this category. Stopping")
            return
        elif current_category is None:
            click.echo("Couldn't find a category with open challenges. Stopping.")
            return

        challenge = challenge_me.get_challenge(current_category, number)
        attempts = challenge_me.get_attempts(current_category, number)

        click.echo('Verifying challenge {1} for category {0}.'.format(current_category, number))
        # TODO: check all attempts
        success, input_text, output_text, command = challenge_me.verify(challenge, attempts[0])

        if success:
            click.secho("Success.", fg='green')
            click.echo("Creating file for next challenge.")
            new_challenge = challenge_me.get_challenge_with_test(category, number + 1)
            challenge_me.create_attempt(new_challenge, language)
        else:
            click.secho('Failure.', fg='red')
            click.echo('Input: {}'.format(input_text))
            click.echo('Result: {}'.format(command.stdout.text.strip()))
            click.echo('Expected: {}'.format(output_text.strip()))

            if command.stderr:
                click.echo('Error: {}'.format(command.stderr.text))

    except ValueError as e:
        click.echo(str(e) + " Stopping.")


@main.command()
@click.argument('category', required=False)
@click.option('--language', default="python", required=False)
def skip(category, language):
    """
    Skipping a challenge.

    Args:
        language:
        category:
    """
    if category:
        number = challenge_me.current_attempt_in_category(category)
    else:
        category, number = challenge_me.current_attempt()

    click.echo('Skipping challenge {1} in category {0}.'.format(category, number))
    new_challenge = challenge_me.get_challenge_with_test(category, number + 1)
    challenge_me.create_attempt(new_challenge, language)


if __name__ == "__main__":
    main()
