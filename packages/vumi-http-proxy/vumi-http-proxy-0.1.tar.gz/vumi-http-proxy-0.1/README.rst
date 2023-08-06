vumi-http-proxy
====

Black & White listing HTTP Proxy for Vumi Sandbox HTTP requests

|vumi-proxy-ci| |vumi-proxy-cover| |vumi-proxy-docs|

.. |vumi-proxy-ci| image:: https://travis-ci.org/praekelt/vumi-http-proxy.svg?branch=develop
    :alt: Vumi-http-proxy Travis CI build status
    :scale: 100%
    :target: https://travis-ci.org/praekelt/vumi-http-proxy

.. |vumi-proxy-cover| image:: https://coveralls.io/repos/github/praekelt/vumi-http-proxy/badge.svg?branch=develop
    :alt: Vumi-http-proxy coverage on Coveralls
    :scale: 100%
    :target: https://coveralls.io/r/praekelt/vumi-http-proxy?branch=develop

.. |vumi-proxy-docs| image:: https://readthedocs.org/projects/queen-of-ni/badge/?version=latest
	:target: http://queen-of-ni.readthedocs.org/en/latest/?badge=latest
	:alt: Documentation Status
	:scale: 100%

To build this locally::

	$ virtualenv ve
	$ source ve/bin/activate
	(ve)$ pip install -e .

To run using default ip and port configuration::

	(ve)$ twistd -n vumi_http_proxy --blacklist=BLACKLISTFILENAME

Alternatively::

	(ve)$ queen-of-ni --blacklist BLACKLISTFILENAME

To run using manual configuration::

	(ve)$ twistd -n vumi_http_proxy --interface=IPADDRESS --port=PORTNO --blacklist=BLACKLISTFILENAME

Alternatively::

	(ve)$ queen-of-ni --interface IPADDRESS --port PORTNO --blacklist BLACKLISTFILENAME

For help::

	(ve)$ queen-of-ni --help
