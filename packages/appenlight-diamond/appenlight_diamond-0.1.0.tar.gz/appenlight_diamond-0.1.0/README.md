# appenlight_diamond
Python-Diamond handler for App Enlight

Usage
-----

If not using diamond version that comes with bundled handler,
you first need to install the package:

    pip install appenlight_diamond

Then you need to add the handler to your `diamond.conf` handler section:

    # Handlers for published metrics.
    handlers = diamond.handler.appenlight.AppenlightMetricHandler, ..., diamond.handler.archive.ArchiveHandler

If your installation doesn't ship the handler yet the handler and you installed it
on your own, line needs to be slightly different:

    # Handlers for published metrics.
    handlers = appenlight_diamond.AppenlightMetricHandler, ..., diamond.handler.archive.ArchiveHandler

Finally, you need to add a configuration section:

    [[AppenlightMetricHandler]]
    apikey = PRIVATE_API_KEY
    #server = http://optional.custom.server.com

`apikey` is mandatory, `server` is optional and by default
*https://api.appenlight.com* will be used as default value.
