/*
 * View model for OctoPrint-Terminalstats
 *
 * Author: Gina Häußge
 * License: AGPLv3
 */
$(function() {
    function TerminalstatsViewModel(parameters) {
        var self = this;

        self.receivedLinesElement = undefined;
        self.sendLinesElement = undefined;
        self.receivedBytesElement = undefined;
        self.sendBytesElement = undefined;

        self.onStartup = function() {
            self.receivedLinesElement = $('<span class="plugin-terminalstats-stat"></span>');
            self.sendLinesElement = $('<span class="plugin-terminalstats-stat"></span>');
            self.receivedBytesElement = $('<span class="plugin-terminalstats-stat"></span>');
            self.sendBytesElement = $('<span class="plugin-terminalstats-stat"></span>');

            var sendField = $('<span class="span6"></span>');
            sendField.append("Sent: ")
            sendField.append(self.sendLinesElement);
            sendField.append(" lines/s");
            sendField.append(" | ");
            sendField.append(self.sendBytesElement);
            sendField.append(" B/s");

            var receivedField = $('<span class="span6" style="text-align: right"></span>');
            receivedField.append("Recv: ")
            receivedField.append(self.receivedLinesElement);
            receivedField.append(" lines/s");
            receivedField.append(" | ");
            receivedField.append(self.receivedBytesElement);
            receivedField.append(" B/s");

            var container = $('<div class="plugin-terminalstats-container row-fluid"></div>');
            container.append(sendField);
            container.append(receivedField);

            container.insertBefore($('#terminal-sendpanel'));
        }

        self.onDataUpdaterPluginMessage = function(plugin, message) {
            if (plugin !== "terminalstats") return;

            self.receivedLinesElement.text(message.receive_rate_lines);
            self.receivedBytesElement.text(message.receive_rate_bytes);
            self.sendLinesElement.text(message.send_rate_lines);
            self.sendBytesElement.text(message.send_rate_bytes);
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: TerminalstatsViewModel,
        dependencies: [ ],
        elements: [ ]
    });
});
