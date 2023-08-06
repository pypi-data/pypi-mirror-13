import click
import hashlib

import oyster


@click.group()
def cli():
    pass

@click.command()
@click.option('--infile', '-i')
@click.option('--outfile', '-o', default='outfile.enc')
@click.option('--keyfile', '-k')
def encrypt(infile, outfile, keyfile):
    """ Encrypt a file """

    with open(keyfile, 'r') as f:
        key = hashlib.sha256(f.read().encode('utf-8')).digest()
    oyster.encrypt(infile, outfile, key)

cli.add_command(encrypt)


if __name__ == '__main__': # pragma: no cover
    cli()
