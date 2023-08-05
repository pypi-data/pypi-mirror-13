<h1 id="tgbotplug">tgbotplug</h1>
<p><a href="https://travis-ci.org/fopina/tgbotplug"><img src="https://travis-ci.org/fopina/tgbotplug.svg" alt="Build Status" /></a></p>
<p>tgbotplug is meant to be an easy-to-extend telegram bot built around <a href="https://github.com/datamachine/twx.botapi">twx.botapi</a>.</p>
<p>Using tgbotplug, after choosing/developing your plugins, is as simple as:</p>
<div class="sourceCode"><pre class="sourceCode python"><code class="sourceCode python"><span class="im">import</span> tgbot
tgbot.TGBot(
  <span class="st">&#39;YOUR_BOT_TOKEN&#39;</span>,
  plugins<span class="op">=</span>[
    Plugin1(),
    ...,
    PluginN(),
  ],
).run()</code></pre></div>
<p>Plugins should inherit <code>tgbot.TGPluginBase</code>and implement <code>list_commands()</code> (and the methods mapped in its result).</p>
<p>Plugin examples can be found in <a href="https://github.com/fopina/tgbotplug-plugins">tgbotplug-plugins</a>.</p>
<p>Also, a few full bot examples (using webhooks and prepared to deploy in OpenShift): * <a href="https://github.com/fopina/tgbot-buttiebot">ButtieBot</a> * <a href="https://github.com/fopina/tgbot-buttiebot">PriberamBot</a> * <a href="https://github.com/pmpfl/indieshufflebot">IndieShuffleBot</a></p>
