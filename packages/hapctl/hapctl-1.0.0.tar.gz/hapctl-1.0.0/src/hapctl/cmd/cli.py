# -*- coding: utf-8 -*-

from socket import error as socket_error
import click
from hapctl import haproxy


@click.command()
@click.option('--socket', default='/run/haproxy/admin.sock', help='HAProxy Control Socket')
@click.argument('command')
def cli(socket, command):
    try:
        hap = haproxy.HAProxyStats(socket)
        result = hap.execute(command)

        click.echo(result)
    except socket_error as serr:
        click.echo("Socket error: %s" % serr)
