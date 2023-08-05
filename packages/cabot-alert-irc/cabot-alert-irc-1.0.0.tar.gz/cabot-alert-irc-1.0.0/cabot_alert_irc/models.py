# -*- coding: utf-8 -*-

from django.db import models
from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from os import environ as env

from irc3.plugins.command import command
from irc3.compat import asyncio
import irc3

# Plugin for irc3 that connects, say its message and disconnect
@irc3.plugin
class CabotPlugin(object):
    def __init__(self, bot):
        self.bot = bot

    @irc3.event(irc3.rfc.JOIN)
    def connect(self, mask, channel, **kw):
        # log only when the bot connect and disconect right after
        if mask.nick == self.bot.nick:
            self.bot.privmsg(channel, self.bot.config.message)
            self.disconnect()

    # Quit the server and call the end of the asyncio loop
    def disconnect(self):
        self.bot.quit()
        self.bot.config.end_callback.set_result('OK')


class IRCAlert(AlertPlugin):
    name = " IRC"
    author = "nobe4"
    config = {}

    # Check if the bot should alert
    # Inspired by bonniejools/cabot-alert-hipchat
    def shouldAlert(self, service):
        alert = True
        if service.overall_status == service.WARNING_STATUS:
            alert = False  # Don't alert at all for WARNING
        elif service.overall_status == service.ERROR_STATUS:
            if service.old_overall_status in (service.ERROR_STATUS,
                                              service.ERROR_STATUS):
                alert = False  # Don't alert repeatedly for ERROR
        elif service.overall_status == service.PASSING_STATUS:
            alert = False  # Don't alert when passing
        return alert

    # Create the asyncio loop and irc3 bot with current file plugin (matching
    # CabotPlugin defined above)
    def bootstrapIrc3(self):
        # Create the asyncio loop
        loop = asyncio.get_event_loop()
        end_callback = asyncio.Future()

        # save the end method to be called after posting the message
        self.config['end_callback'] = end_callback
        self.config['includes'] = [__name__]

        # Create the bot and run it once
        sender = irc3.IrcBot.from_config(self.config)
        sender.run(forever=False)

        # set the asyncio resolve Future
        loop.run_until_complete(end_callback)

    # Get the requirement from cabot environment
    def configure(self, service):
        self.config = dict(
            host=env.get('IRC_HOST'),
            port=env.get('IRC_PORT'),
            nick=env.get('IRC_BOT_NICK'),
            autojoins='#' + env.get('IRC_ROOM'),
            message=service.overall_status + ' Alert : ' + service.name
        )

    def send_alert(self, service, users, duty_officers):
        if self.shouldAlert(service):
            self.configure(service)
            self.bootstrapIrc3()


class IRCAlertUserData(AlertPluginUserData):
    name = "IRC Plugin"
