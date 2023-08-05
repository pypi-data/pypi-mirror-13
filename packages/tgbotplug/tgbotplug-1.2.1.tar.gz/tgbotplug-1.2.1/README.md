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
[![Build Status](https://travis-ci.org/fopina/tgbotplug.svg)](https://travis-ci.org/fopina/tgbotplug)

1. [Documentation](#documentation)
2. [VirtualLife Examples](#virtuallife-examples)

## Documentation

Plugins should inherit `tgbot.TGPluginBase`and implement `list_commands()` (and the methods mapped in its result).

Documentation is a bit scarse (*== None*) at the moment so please focus on the [plugin examples](https://github.com/fopina/tgbotplug-plugins) and the [VirtualLife Examples](#virtuallife-examples) for now!

## VirtualLife Examples

* [PriberamBot](https://github.com/fopina/tgbot-buttiebot) - uses webhooks, packaged for Heroku
* [ButtieBot](https://github.com/fopina/tgbot-buttiebot) - uses webhooks, sends photos, packaged for OpenShift
* [IndieShuffleBot](https://github.com/pmpfl/indieshufflebot) - uses webhooks, sends audio, packaged for OpenShift
