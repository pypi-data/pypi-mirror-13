#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This software is licensed as described in the README.rst and LICENSE files,
# which you should have received as part of this distribution.

from rpi_doorman.rpi_doorman import Doorman
import gammu
import time
import logging


class DoormanGammu(Doorman):

    cell_phone = None
    ringing_time = 10

    def _setup_cell_phone(self):
        # TODO: when separated here, second call keeps ringing forever!

        # Create object for talking with phone
        self.cell_phone = gammu.StateMachine()
        # Read the configuration (~/.gammurc)
        self.cell_phone.ReadConfig()
        # Connect to the phone
        self.cell_phone.Init()

    def __init__(self, args=[]):
        # self._setup_cell_phone()
        super(DoormanGammu, self).__init__(args)

    def call(self):
        if hasattr(self.args, 'number') and self.args.number:
            logging.debug('Connecting to phone')

            try:
                # Create object for talking with phone
                self.cell_phone = gammu.StateMachine()
                # Read the configuration (~/.gammurc)
                self.cell_phone.ReadConfig()
                # Connect to the phone
                self.cell_phone.Init()

            except gammu.GSMError as e:
                logging.error(e)

            else:
                logging.debug('Dialing number: %s', self.args.number)
                self.cell_phone.DialVoice(self.args.number)
                logging.debug('Keep it ringing for %s seconds', self.ringing_time)
                time.sleep(self.ringing_time)
                self.cell_phone.PressKey('R', True)
                logging.debug('Hangup the call')

    def callback_sensor_read(self):
        super(DoormanGammu, self).callback_sensor_read()
        self.call()
