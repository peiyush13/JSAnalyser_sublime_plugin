
"use strict";


module.exports = {
    meta: {
        docs: {
            description: "disallow variable starting without BMC prefix",
            category: "Possible Errors",
            recommended: true
        },
        schema: [ ]
    },



    create: function(context) {

        const reported = [];
        
        function report(node) {
            if (reported.indexOf(node) < 0) {
                reported.push(node);
                context.report({ node, message: "Identifier '{{name}}' is not starting with BMC prefix.", data: { name: node.name } });
            }
        }

        return {

            Identifier(node) {
                const name=node.name;
                const input="BMC";
                 if (name.substring(0, input.length) === input)
                    return;    
                 else
                    report(node);   
            }
        }
    }
}
 