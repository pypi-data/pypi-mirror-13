#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import datetime
import re
import sys
import subprocess

__author__ = 'Matthieu Gallet'

ZERO = datetime.timedelta(0)

T61_RE = re.compile(r'^([A-Z][a-z]{2}) {1,2}(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2}) (\d{4}).*$')


def t61_to_time(d):
    """
    >>> t61_to_time('Jul  8 14:01:58 2037 GMT') is not None
    True
    >>> t61_to_time('Jul  8 14:01:58 2037 GMT').year
    2037

    :param d:
    :type d:
    :return:
    :rtype:
    """
    matcher = T61_RE.match(d)
    if matcher:
        groups = matcher.groups()
        month = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9,
                 'Oct': 10, 'Nov': 11, 'Dec': 12}[groups[0]]
        return datetime.datetime(int(groups[5][-2:]) + 2000, month, int(groups[1]), int(groups[2]), int(groups[3]),
                                 int(groups[4]))
    return None


def main():
    parser = argparse.ArgumentParser(description='Check certificate.')
    parser.add_argument('path', default=[], nargs='+')
    parser.add_argument('--CApath', default=None)
    parser.add_argument('--CAfile', default=None)
    parser.add_argument('-D', default=None, type=int)
    parser.add_argument('-C', default=None, type=int)
    args = parser.parse_args()
    exit_text = ''
    exit_code = 0
    for path in args.path:
        command = ['openssl', 'verify']
        if args.CApath:
            command += ['--CApath', args.CApath]
        if args.CAfile:
            command += ['--CAfile', args.CAfile]
        command += [path, ]
        p = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        p.communicate()
        local_exit_code = 0
        if p.returncode != 0:
            local_exit_code = 2
            local_text = {2: "unable to get issuer certificate",
                          3: "the CRL of a certificate could not be found.",
                          4: "the certificate signature could not be decrypted.",
                          5: "the CRL signature could not be decrypted",
                          6: "the public key in the certificate SubjectPublicKeyInfo could not be read.",
                          7: "the signature of the certificate is invalid.",
                          8: "the signature of the certificate is invalid.",
                          9: "the certificate is not yet valid: the notBefore date is after the current time.",
                          }.get(p.returncode, 'invalid certificate')
            exit_text += 'CRITICAL - %s is invalid: %s\n' % (path, local_text)
        elif args.D or args.C:
            command = ['openssl', 'x509', '-enddate', '-noout', '-in', path, ]
            p = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = p.communicate()
            stdout = stdout.decode('utf-8')
            end_date = t61_to_time(stdout.partition('=')[2].strip())
            if args.C:
                after_now = datetime.datetime.now() + datetime.timedelta(args.C)
                if end_date < after_now:
                    local_exit_code = 2
                    exit_text += 'CRITICAL - Certificate %s will expire on %s\n' % \
                                 (path, end_date.strftime('%m/%d/%Y %H:%M'))
            if args.D and local_exit_code == 0:
                after_now = datetime.datetime.now() + datetime.timedelta(args.D)
                if end_date < after_now:
                    local_exit_code = 1
                    exit_text += 'WARNING - Certificate %s will expire on %s\n' % \
                                 (path, end_date.strftime('%m/%d/%Y %H:%M'))
        if local_exit_code == 0:
            exit_text += 'OK - certificate is valid\n'
        exit_code = max(local_exit_code, exit_code)
    print(exit_text.strip())
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
