({
    mainConfigFile: '../www/js/main.js',
    
    //Duplicate baseUrl here because otherwise the paths
    //reference below will not work out.
    baseUrl: '../www/js',

    paths: {
        'alpha': 'sub/alpha'
    },
    enabled: {
        beta: true
    },

    //Made up values just to test nested merging skip logic.
    someRegExp: /bar/,
    someFunc: function () {},
    someArray: ['one', 'two'],

    name: 'main',
    out: '../main-built.js',
    optimize: 'none'
})
