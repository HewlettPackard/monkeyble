# Copyright 2022 Hewlett Packard Enterprise Development LP
"""
Ansible version detection and feature flags.
Centralizes all version-specific behavior so the rest of Monkeyble
doesn't need to check versions directly.
"""

from ansible.release import __version__ as ansible_version

ANSIBLE_VERSION = tuple(int(x) for x in ansible_version.split(".")[:2])
ANSIBLE_2_19_PLUS = ANSIBLE_VERSION >= (2, 19)

try:
    from ansible._internal._datatag._tags import TrustedAsTemplate

    HAS_DATATAG = True
except ImportError:
    TrustedAsTemplate = None
    HAS_DATATAG = False
