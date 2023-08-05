# coding=utf-8
"""
hangman.__main__
~~~~~~~~~~~~~~~~

Entry point for ``hangman`` command.
"""


import click

from hangman import controller


@click.command()
def cli():
    """
    Start a new game.
    """
    controller.game_loop()


if __name__ == '__main__':
    cli()  # pragma: no cover
