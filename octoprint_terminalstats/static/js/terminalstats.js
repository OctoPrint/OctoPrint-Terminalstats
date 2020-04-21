/*
 * View model for OctoPrint-Terminalstats
 *
 * Author: Gina Häußge
 * License: AGPLv3
 */
$(function() {
    function TerminalstatsViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        self.receivedLines = ko.observable();
        self.sendLines = ko.observable();
        self.receivedBytes = ko.observable();
        self.sendBytes = ko.observable();
        self.receivedPeak = ko.observable();
        self.sendPeak = ko.observable();

        self.receivedSparkElement = undefined;
        self.sendSparkElement = undefined;

        self.receivedStats = ko.pureComputed(function() {
            return '' + self.receivedLines() + 'L/s | ' + self.receivedBytes() + 'B/s | ' + self.receivedPeak() + 'B/s'
        });
        self.sendStats = ko.pureComputed(function() {
            return '' + self.sendLines() + 'L/s | ' + self.sendBytes() + 'B/s | ' + self.sendPeak() + 'B/s'
        });

        self.onStartup = function() {
            log.info("Oh Hai!");
            var wrapper = $("#plugin_terminalstats_snippet_wrapper");
            wrapper.insertBefore($('#terminal-sendpanel'));

            self.receivedSparkElement = $("#plugin_terminalstats_snippet_spark_received");
            self.sendSparkElement = $("#plugin_terminalstats_snippet_spark_send");
        };

        self.onDataUpdaterPluginMessage = function(plugin, message) {
            if (plugin !== "terminalstats") return;

            self.receivedLines(message.receive_rate_lines);
            self.receivedBytes(message.receive_rate_bytes);
            self.receivedPeak(message.receive_rate_max);
            self.sendLines(message.send_rate_lines);
            self.sendBytes(message.send_rate_bytes);
            self.sendPeak(message.send_rate_max);

            var options = {type: 'line', fillColor: undefined, chartRangeMin: 0, zeroAxis: false};
            self.receivedSparkElement.sparkline(message.receive_rate_history, $.extend({chartRangeMax: message.receive_rate_max}, options));
            self.sendSparkElement.sparkline(message.send_rate_history, $.extend({chartRangeMax: message.send_rate_max}, options));
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: TerminalstatsViewModel,
        dependencies: [ "settingsViewModel" ],
        elements: [ "#plugin_terminalstats_snippet" ]
    });
});
