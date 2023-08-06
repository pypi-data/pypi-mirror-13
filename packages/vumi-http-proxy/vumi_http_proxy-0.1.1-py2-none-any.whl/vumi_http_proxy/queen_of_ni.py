#!/usr/bin/env python

import click
from vumi_http_proxy import http_proxy
from vumi_http_proxy import config_reader


@click.command()
@click.option('--interface', default='0.0.0.0', help='eg 0.0.0.0')
@click.option('--port', default=8080, help='eg 80')
@click.option('--configfile', default=None,
              help='example file: ./docs/proxy_config.yml')
def cli(interface, port, configfile):
    """This script runs vumi-http-proxy on <interface>:<port>
    with the specified blacklist"""
    blacklist, dns_servers = config_reader.read_config(configfile)
    interface = str(interface)
    click.echo("Starting connection to %s:%d" % (interface, port))
    i = http_proxy.Initialize(blacklist, dns_servers, interface, port)
    i.main()


if __name__ == '__main__':
    cli()
