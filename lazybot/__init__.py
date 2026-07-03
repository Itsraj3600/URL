"""Compatibility layer for legacy lazybot imports."""

from cinebot import Cine3600Bot

multi_clients = {0: Cine3600Bot}
work_loads = {0: 0}
LazyPrincessBot = Cine3600Bot


def create_bot_client():
    return Cine3600Bot