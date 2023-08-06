"""
This file is part of Ludolph: Doorman plugin

See the LICENSE file for copying permission.
"""
import time
from rpi_doorman.rpi_doorman import Doorman

from ludolph_doorman import __version__
from ludolph.command import CommandError, command
from ludolph.plugins.plugin import LudolphPlugin
from ludolph.web import webhook, request, abort


class Serve(LudolphPlugin):
    """
    Ludolph: Doorman, plugin commands.
    """
    __version__ = __version__

    # noinspection PyUnusedLocal
    @command
    def door_state(self, msg):
        """
        Doorman get current state of door (output from get_door_state function).

        RPi.Doorman is using adafruit magnetic contact switch (door sensor), and
        monitor door state.

        More info: https://github.com/ricco386/rpi-doorman

        Usage: door-state
        """
        d = Doorman()
        return d.get_door_state()

    @webhook('/doorman_update', methods=('POST',))
    def doorman_update(self):
        """
        Webhook to receive updates from Doorman service if sensor status change.
        """
        user = request.forms.get('user', None)
        msg = request.forms.get('msg', None)

        if not user:
            abort(400, 'Missing user parameter in request')

        if not msg:
            abort(400, 'Missing msg parameter in request')

        self.xmpp.msg_send(user, msg)

        return 'Message sent'
