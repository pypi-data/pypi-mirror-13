/*global module, process, require*/

var htmlbars = require('./node_modules/htmlbars/dist/cjs/htmlbars-syntax.js');

/**
 * Pybabel extractor for HTMLBars templates.
 *
 * Uses the HTMLBars parser to generate an AST, which is descended to extract
 * translatable strings. The result is written to stdout as JSON.
 */
module.exports = {
    start: function () {
        this.init();
        this.communicate('WAITING FOR COMMAND');
    },

    init: function () {
        this.received_data = "";
        this.output = [];
        /*
         * The `MustacheStatement` extraction code can be used for
         * `SubExpression` as well.
         */
        this.extractSubExpression = this.extractMustacheStatement;
    },

    communicate: function (message) {
        process.stdout.write('PYBABEL_HTMLBARS RESPONSE:' + message);
    },

    flush: function () {
        var parsed_data = htmlbars.parse(this.received_data);
        this.extract(parsed_data);

        this.communicate('SENDING OUTPUT');
        process.stdout.write(JSON.stringify(this.output));
        this.communicate('OUTPUT END');
    },

    /**
     * Run the appropriate extractor on `node` according to its type.
     */
    extract: function (node) {
        var extractor = 'extract' + node.type;

        if (this[extractor]) {
            this[extractor](node);
        }
    },

    /**
     * Extract strings from the body of the program contained in `node`.
     */
    extractProgram: function (node) {
        for (var child of node.body) {
            this.extract(child);
        }
    },

    /**
     * Extract strings from the attributes and children of an HTML element
     * node.
     */
    extractElementNode: function (node) {
        for (var attribute of node.attributes) {
            this.extract(attribute.value);
        }

        for (var child of node.children) {
            this.extract(child);
        }
    },

    /**
     * Extract strings from a block statement. Block statements may have an
     * inverse (such as `else`); extract strings from those too. Also extract
     * strings from any binding pairs in the block statement.
     */
    extractBlockStatement: function (node) {
        this.extract(node.program);

        if (node.inverse) {
            this.extract(node.inverse);
        }

        for (var pair of node.hash.pairs) {
            this.extract(pair.value);
        }
    },

    /**
     * Extract every part of a concatenated statement.
     */
    extractConcatStatement: function (node) {
        for (var part of node.parts) {
            this.extract(part);
        }
    },

    /**
     * The core of the extractor, extracts translatable strings from Mustache
     * statements and sub-expressions. Currently supported string formats are:
     *
     * - Mustache statements:
     *   - Singular string: {{_ "Translate me!"}}
     *   - Plural string: {{n_ n "Translate me!" "Translate us!"}}
     *
     * - Sub-expressions:
     *   - Singular string: {{foo (_ "Translate me!")}}
     *   - Plural string: {{foo (n_ n "Translate me!" "Translate us!")}}
     */
    extractMustacheStatement: function (node) {
        var param;
        var param_singular;
        var param_plural;
        var param_context;

        // Singular strings
        if (node.path.original === '_') {
            param = node.params[0];

            if (param && param.type === 'StringLiteral') {
                this.output.push({
                    line_number: node.loc.start.line,
                    content: param.value,
                    funcname: 'gettext',
                });
            }
        }

        // Plural strings
        else if (node.path.original === 'n_') {
            param_singular = node.params[1];
            param_plural = node.params[2];

            if (param_singular &&
                param_singular.type === 'StringLiteral' &&
                param_plural &&
                param_plural.type === 'StringLiteral') {
                this.output.push({
                    line_number: node.loc.start.line,
                    content: param_singular.value,
                    alt_content: param_plural.value,
                    funcname: 'ngettext',
                });
            }
        }

        // With context
        else if (node.path.original === 'p_') {
            param_context = node.params[0];
            param = node.params[1];

            if (param_context && param_context.type === 'StringLiteral' &&
                param && param.type === 'StringLiteral') {
                this.output.push({
                    line_number: node.loc.start.line,
                    content: param_context.value,
                    alt_content: param.value,
                    funcname: 'pgettext',
                });
            }
        }

        // Nested expressions
        for (param of node.params) {
            this.extract(param);
        }

        // Pair values
        for (var pair of node.hash.pairs) {
            this.extract(pair.value);
        }
    },
};
