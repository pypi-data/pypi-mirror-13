options = JSON.stringify(options);

options = JSON.parse(options, function(key, value) {

    if (value && (typeof value==="string")) {

        // replace spaces then newline characters
        if (value.replace(/\s+/g, '').replace(/\r?\n|\r/g, '').substr(0,8) == "function") {
            var startBody = value.indexOf('{') + 1;
            var endBody = value.lastIndexOf('}');
            var startArgs = value.indexOf('(') + 1;
            var endArgs = value.indexOf(')');

            return new Function(value.substring(startArgs, endArgs),
                                value.substring(startBody, endBody));
        }

        // replace spaces then newline characters
        if (value.replace(/\s+/g, '').replace(/\r?\n|\r/g, '').substr(0,9) == "(function") {
            var startBody = value.indexOf('{') + 1;
            var endBody = value.lastIndexOf('}');
            var startArgs = value.indexOf('(', 1) + 1;
            var endArgs = value.indexOf(')');

            var func = new Function(value.substring(startArgs, endArgs),
                                    value.substring(startBody, endBody));
            return func();
        }
    }

    return value;
});
