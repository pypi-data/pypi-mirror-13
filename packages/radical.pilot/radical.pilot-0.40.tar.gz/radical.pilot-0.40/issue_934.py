#!/usr/bin/env python

import netifaces

def hostip(req=None, logger=None):
    """
    Look up the ip number for a given requested interface name.
    If interface is not given, do some magic.
    """

    # List of interfaces that we probably dont want to bind to by default
    black_list = ['eth0', 'lo', 'sit0', 'lo']

    # Known intefaces in preferred order
    sorted_preferred = [
        'ipogif0', # Cray's
        'br0', # SuperMIC
    ]

    # Get a list of all network interfaces
    all = netifaces.interfaces()

    print "Network interfaces detected: %s" % all

    pref = None
    # If we got a request, see if it is in the list that we detected
    if req and req in all:
        # Requested is available, set it
        pref = req
    else:
        # No requested or request not found, create preference list
        potentials = [iface for iface in all if iface not in black_list]

    # If we didn't select an interface already
    if not pref:
        # Go through the sorted list and see if it is available
        for iface in sorted_preferred:
            if iface in all:
                # Found something, get out of here
                pref = iface
                break

    # If we still didn't find something, grab the first one from the
    # potentials if it has entries
    if not pref and potentials:
        pref = potentials[0]

    # If there were no potentials, see if we can find one in the blacklist
    if not pref:
        for iface in black_list:
            if iface in all:
                pref = iface

    print "Network interface  selected: %s" % pref

    # Use IPv4, because, we can ...
    af = netifaces.AF_INET
    ni = netifaces.ifaddresses(pref)
    ip = ni[af][0]['addr']

    return ip

print hostip()

