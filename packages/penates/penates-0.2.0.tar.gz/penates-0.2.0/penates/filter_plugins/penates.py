# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib
import random
import re
import crypt
import netaddr
import unicodedata

__author__ = 'Matthieu Gallet'


def hostname_to_dn(fqdn):
    """Convert a fqdn to its LDAP form

    >>> hostname_to_dn("test.example.com")
    u'dc=test,dc=example,dc=com'

    """
    return ','.join(['dc=' + x for x in fqdn.split('.')])


def hostname_to_dn_first(fqdn):
    """Get the first component of a domain name

    >>> hostname_to_dn_first("test.example.com")
    u'test'

    """
    return fqdn.split('.')[0]


def str_to_hex(text):
    """

    >>> str_to_hex("toto")
    u'{HEX}746f746f'
    """
    return '{HEX}' + ''.join(['%x' % ord(x) for x in text])


def subnet_mask(subnet):
    """
    >>> subnet_mask('192.168.56.1/24')
    '255.255.255.0'
    """
    network = netaddr.IPNetwork(subnet)
    return str(network.netmask)


def subnet_mask_len(subnet):
    """
    >>> subnet_mask_len('192.168.56.1/24')
    '24'
    """
    network = netaddr.IPNetwork(subnet)
    return str(network.prefixlen)


def subnet_address(subnet):
    """
    >>> subnet_address('192.168.56.1/24')
    '192.168.56.0'
    """
    network = netaddr.IPNetwork(subnet)
    return str(network.network)


def subnet_broadcast(subnet):
    """
    >>> subnet_broadcast('192.168.56.1/24')
    '192.168.56.255'
    """
    network = netaddr.IPNetwork(subnet)
    return str(network.broadcast)


def subnet_start(subnet):
    """
    >>> subnet_start('192.168.56.1/24')
    '192.168.56.32'
    """
    network = netaddr.IPNetwork(subnet)
    size = 32 if network.version == 4 else 128
    return str(network.network + 2 ** max(size - network.prefixlen - 3, 0))


def subnet_end(subnet):
    """
    >>> subnet_end('192.168.56.1/24')
    '192.168.56.254'
    """
    network = netaddr.IPNetwork(subnet)
    size = 32 if network.version == 4 else 128
    return str(network.network - 2 + 2 ** (size - network.prefixlen))


def reverse_subnet(subnet):
    """
    >>> reverse_subnet('192.168.56.0/24')
    u'56.168.192.in-addr.arpa'
    """
    network = netaddr.IPNetwork(subnet)
    return network.network.reverse_dns[:-1].partition('.')[2]


def subnet_version(subnet):
    """
    >>> subnet_version('192.168.56.0/24')
    4
    """
    return netaddr.IPNetwork(subnet).version


def slugify(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def indexed_fqdn(value, host_list):
    """
    >>> indexed_fqdn('host_1', ['host_0', 'host_1', 'host_2']) == '02'
    True
    """
    return '%02d' % (host_list.index(value) + 1)


def generate_salt():
    salt_set = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789./')
    salt = 16 * ' '
    return ''.join([random.choice(salt_set) for c in salt])


def mkpasswd(passwd, algo='SHA-256'):
    algos = {'SHA-512': '$6$', 'SHA-256': '$5$', 'MD5': '$1$', 'DES': ''}
    salt = generate_salt()
    result = crypt.crypt(passwd, algos[algo] + salt)
    return result


def randomize_passwd(passwd):
    return hashlib.sha256(passwd.encode('utf-8')).hexdigest()


def penates_kcurl(directory_fqdn, extra_url, dest_file=None, binary_file=None):
    """Return the command line for an authenticated cURL call to the penatesserver

    :param directory_fqdn: fqdn of the PenatesServer
    :param extra_url:
    """
    extra_args = ''
    if dest_file is not None:
        extra_args += ' -o ' + dest_file
    if binary_file is not None:
        extra_args += ' --data-binary @' + binary_file
    return 'k5start -q -f /etc/host.keytab -U -- curl --anyauth -u : %s https://%s/auth/%s' % \
           (extra_args, directory_fqdn, extra_url)


class FilterModule(object):
    # noinspection PyMethodMayBeStatic
    def filters(self):
        return {'hostname_to_dn': hostname_to_dn,
                'hostname_to_dn_first': hostname_to_dn_first,
                'str_to_hex': str_to_hex,
                'subnet_mask_len': subnet_mask_len,
                'subnet_mask': subnet_mask,
                'subnet_address': subnet_address,
                'subnet_broadcast': subnet_broadcast,
                'subnet_start': subnet_start,
                'subnet_end': subnet_end,
                'reverse_subnet': reverse_subnet,
                'subnet_version': subnet_version,
                'slugify': slugify,
                'indexed_fqdn': indexed_fqdn,
                'mkpasswd': mkpasswd,
                'randomize_passwd': randomize_passwd,
                'penates_kcurl': penates_kcurl,
                }
