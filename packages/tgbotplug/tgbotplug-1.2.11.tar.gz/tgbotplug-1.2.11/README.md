tgbotplug is meant to be an easy-to-extend telegram bot built around [twx.botapi](https://github.com/datamachine/twx.botapi).

Using tgbotplug, after choosing/developing your plugins, is as simple as:

```python
import tgbot
tgbot.TGBot(
  'YOUR_BOT_TOKEN',
  plugins=[
    Plugin1(),
    ...,
    PluginN(),
  ],
).run()
```

## Overview
[![PyPI version](https://badge.fury.io/py/tgbotplug.svg)](https://badge.fury.io/py/tgbotplug) [![Build Status](https://travis-ci.org/fopina/tgbotplug.svg?branch=master)](https://travis-ci.org/fopina/tgbotplug) [![Coverage Status](https://coveralls.io/repos/fopina/tgbotplug/badge.svg?branch=master&service=github)](https://coveralls.io/github/fopina/tgbotplug?branch=master)

1. [Documentation](#documentation)
2. [VirtualLife Examples](#virtuallife-examples)

## Documentation

Plugins should inherit `tgbot.pluginbase.TGPluginBase` and implement `list_commands()` (and the methods mapped in its result).

Documentation is a bit scarse (*== None*) at the moment so please focus on the [plugin examples](https://github.com/fopina/tgbotplug/tree/master/plugin_examples) and the [VirtualLife Examples](#virtuallife-examples) for now!

## VirtualLife Examples

* [PriberamBot](http://fopina.github.io/tgbot-priberambot) - uses webhooks, inline queries, packaged for Heroku
* [ButtieBot](http://fopina.github.io/tgbot-buttiebot) - uses webhooks, sends photos, packaged for OpenShift
* [EuromillionsBot](http://fopina.github.io/tgbot-euromillionsbot) - uses webhooks, inline queries, packaged for OpenShift
* [PushItBot](http://fopina.github.io/tgbot-pushitbot) - uses webhooks, extends tgbotplug Bottle app for extra routes, packaged for OpenShift
* [IndieShuffleBot](http://pmpfl.github.io/indieshufflebot) - uses webhooks, sends audio, packaged for OpenShift
