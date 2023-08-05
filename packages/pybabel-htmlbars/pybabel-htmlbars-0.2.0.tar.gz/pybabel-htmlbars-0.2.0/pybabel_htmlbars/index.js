/*global process, require*/

var extractor = require('./extractor.js');
var fs = require('fs');

process.stdin.resume();
process.stdin.setEncoding('utf8');
process.stdin.on('data', function (chunk) {
    var command;
    var parts;

    if (chunk.indexOf('PYBABEL_HTMLBARS COMMAND') === 0) {
        parts = chunk.split(":");
        command = parts[1].trim();

        if (command === 'PARSE FILE') {
            extractor.init();
            extractor.received_data = fs.readFileSync(parts[2].trim(), {
                encoding: 'utf8'
            });
            extractor.flush();
        }
    }
});

extractor.start();
