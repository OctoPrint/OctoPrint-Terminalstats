# coding=utf-8
from __future__ import absolute_import, unicode_literals, division

import octoprint.plugin
import octoprint.events
import octoprint.util

class TerminalstatsPlugin(octoprint.plugin.AssetPlugin,
                          octoprint.plugin.EventHandlerPlugin):

	INTERVAL = 2.0

	def __init__(self):
		self._sent_lines = 0
		self._sent_bytes = 0
		self._received_lines = 0
		self._received_bytes = 0

		self._timer = None

	def initialize(self):
		self._timer = octoprint.util.RepeatedTimer(self.INTERVAL, self._worker)
		self._timer.start()

	##~~ AssetPlugin mixin

	def get_assets(self):
		return dict(
			js=["js/terminalstats.js"],
			css=["css/terminalstats.css"]
		)

	##~~ EventHandlerPlugin hook

	def on_event(self, event, payload):
		if event == octoprint.events.Events.CONNECTED:
			self._sent_lines = self._sent_bytes = self._received_lines = self._received_bytes = 0

	##~~ Softwareupdate hook

	def get_update_information(self):
		return dict(
			terminalstats=dict(
				displayName="Terminalstats Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="OctoPrint",
				repo="OctoPrint-Terminalstats",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/OctoPrint/OctoPrint-Terminalstats/archive/{target_version}.zip"
			)
		)

	##~~ GCODE line sent hook

	def line_sent_handler(self, comm_instance, phase, cmd, cmd_type, gcode, subcode=None, tags=None, *args, **kwargs):
		self._sent_lines += 1
		self._sent_bytes += len(cmd)

	##~~ GCODE line received hook

	def line_received_handler(self, comm_instance, line, *args, **kwargs):
		self._received_lines += 1
		self._received_bytes += len(line)
		return line

	##~~ helpers

	def _worker(self):
		send_rate_lines = self._sent_lines / self.INTERVAL
		receive_rate_lines = self._received_lines / self.INTERVAL
		send_rate_bytes = self._sent_bytes / self.INTERVAL
		receive_rate_bytes = self._received_bytes / self.INTERVAL
		self._sent_lines = self._sent_bytes = self._received_lines = self._received_bytes = 0

		self._logger.info("Sent rate: {}l/s / {}B/s, received lines: {}l/s / {}B/s".format(send_rate_lines,
		                                                                                   send_rate_bytes,
		                                                                                   receive_rate_lines,
		                                                                                   receive_rate_bytes))
		self._plugin_manager.send_plugin_message(self._identifier, dict(send_rate_lines=send_rate_lines,
		                                                                send_rate_bytes=send_rate_bytes,
		                                                                receive_rate_lines=receive_rate_lines,
		                                                                receive_rate_bytes=receive_rate_bytes))

__plugin_name__ = "Terminalstats Plugin"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = TerminalstatsPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.sent": __plugin_implementation__.line_sent_handler,
		"octoprint.comm.protocol.gcode.received": __plugin_implementation__.line_received_handler
	}

