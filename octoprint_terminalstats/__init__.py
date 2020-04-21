# coding=utf-8
from __future__ import absolute_import, unicode_literals, division

import octoprint.plugin
import octoprint.events
import octoprint.util

from collections import deque

class TerminalstatsPlugin(octoprint.plugin.AssetPlugin,
                          octoprint.plugin.EventHandlerPlugin,
                          octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.printer.PrinterCallback):

	INTERVAL = 2.0
	MAX_HISTORY = 10

	def __init__(self):
		self._sent_lines = 0
		self._sent_bytes = 0
		self._received_lines = 0
		self._received_bytes = 0

		self._sent_history = deque([], self.MAX_HISTORY)
		self._received_history = deque([], maxlen=self.MAX_HISTORY)

		self._sent_max = 0.0
		self._received_max = 0.0

		self._timer = None

		self._interval = None

	def initialize(self):
		self._printer.register_callback(self)

		self._interval = self._settings.get_float(["interval"])
		self._timer = octoprint.util.RepeatedTimer(self.interval, self._worker)
		self._timer.start()

		self._logger.info("Terminal stats timer initialized with an interval of {}s".format(self._interval))

	def interval(self):
		return self._interval

	##~~ AssetPlugin mixin

	def get_assets(self):
		return dict(
			js=["js/terminalstats.js", "js/jquery.sparkline.min.js"],
			css=["css/terminalstats.css"]
		)

	##~~ EventHandlerPlugin mixin

	def on_event(self, event, payload):
		if event == octoprint.events.Events.CONNECTED:
			self._sent_lines = self._sent_bytes = self._received_lines = self._received_bytes = 0
			self._sent_max = self._received_max = 0.0

	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(interval=self.INTERVAL,
		            unit="bytes")

	def on_settings_save(self, data):
		old_interval = self._settings.get_float(["interval"])

		if "interval" in data:
			try:
				data["interval"] = float(data["interval"])
				if data["interval"] < 1:
					raise ValueError("interval must be >= 1")
			except ValueError:
				self._logger.debug("Invalid interval: {!r}".format(data["interval"]))
				del data["interval"]

		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		new_interval = self._settings.get_float(["interval"])
		if old_interval != new_interval:
			self._interval = new_interval

	##~~ TemplatePlugin mixin

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	##~~ PrinterCallback mixin

	def on_printer_add_log(self, data):
		if data.startswith("Send: "):
			self._sent_lines += 1
			self._sent_bytes += len(data) - 6
		elif data.startswith("Recv: "):
			self._received_lines += 1
			self._received_bytes += len(data) - 6

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

	##~~ helpers

	def _worker(self):
		interval = self._settings.get_float(["interval"])

		send_rate_lines = self._sent_lines / interval
		receive_rate_lines = self._received_lines / interval
		send_rate_bytes = self._sent_bytes / interval
		receive_rate_bytes = self._received_bytes / interval
		self._sent_lines = self._sent_bytes = self._received_lines = self._received_bytes = 0

		self._logger.info("Sent rate: {}l/s / {}B/s, received lines: {}l/s / {}B/s".format(send_rate_lines,
		                                                                                   send_rate_bytes,
		                                                                                   receive_rate_lines,
		                                                                                   receive_rate_bytes))
		self._sent_history.append(send_rate_bytes)
		self._received_history.append(receive_rate_bytes)
		self._sent_max = max(self._sent_max, send_rate_bytes)
		self._received_max = max(self._received_max, receive_rate_bytes)

		self._plugin_manager.send_plugin_message(self._identifier, dict(send_rate_lines=send_rate_lines,
		                                                                send_rate_bytes=send_rate_bytes,
		                                                                receive_rate_lines=receive_rate_lines,
		                                                                receive_rate_bytes=receive_rate_bytes,
		                                                                send_rate_history=list(self._sent_history),
		                                                                receive_rate_history=list(self._received_history),
		                                                                send_rate_max=self._sent_max,
		                                                                receive_rate_max=self._received_max))

__plugin_name__ = "Terminalstats Plugin"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = TerminalstatsPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

