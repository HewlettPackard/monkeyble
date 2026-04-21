# Copyright 2022 Hewlett Packard Enterprise Development LP
"""
Monkeyble templating abstraction.
Wraps Ansible's Templar + data tagging so callers don't need to know
about tag_values or version-specific API differences.
"""

from typing import Any

from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

from plugins.module_utils.ansible_compat import HAS_DATATAG, TrustedAsTemplate


class MonkeybleTemplar:
    """Abstraction over Ansible's Templar that handles data tagging transparently."""

    def __init__(self, variables: dict = None):
        self._variables = variables or {}
        self._templar = Templar(loader=DataLoader(), variables=self._variables)

    def template(self, value: Any) -> Any:
        """Template a value, applying data tagging automatically."""
        return self._templar.template(self._prepare(value))

    def _prepare(self, value: Any):
        """Recurse through a data structure and tag all strings.
        Only needed for Ansible >= 2.19 which introduced data tagging."""
        if not HAS_DATATAG:
            return value
        if isinstance(value, list):
            return [self._prepare(v) for v in value]
        elif isinstance(value, dict):
            return {k: self._prepare(v) for k, v in value.items()}
        elif isinstance(value, str):
            return TrustedAsTemplate().tag(value)
        return value
