requirejs.config({
    'something/else': 'ok',
    _another_thing: 'ok',
    good: true,
    bad: false,
    baseUrl: 'some/thing',
    paths: {
        newlyAdded: 'some/added/path'
    }
});
//DO NOT put a comment first in this file. Need to test 0 position requirejs.config.
