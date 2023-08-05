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
<h2 id="overview">Overview</h2>
<p><a href="https://badge.fury.io/py/tgbotplug"><img src="https://badge.fury.io/py/tgbotplug.svg" alt="PyPI version" /></a> <a href="https://travis-ci.org/fopina/tgbotplug"><img src="https://travis-ci.org/fopina/tgbotplug.svg?branch=master" alt="Build Status" /></a> <a href="https://coveralls.io/github/fopina/tgbotplug?branch=master"><img src="https://coveralls.io/repos/fopina/tgbotplug/badge.svg?branch=master&amp;service=github" alt="Coverage Status" /></a></p>
<ol style="list-style-type: decimal">
<li><a href="#documentation">Documentation</a></li>
<li><a href="#virtuallife-examples">VirtualLife Examples</a></li>
</ol>
<h2 id="documentation">Documentation</h2>
<p>Plugins should inherit <code>tgbot.TGPluginBase</code>and implement <code>list_commands()</code> (and the methods mapped in its result).</p>
<p>Documentation is a bit scarse (<em>== None</em>) at the moment so please focus on the <a href="https://github.com/fopina/tgbotplug-plugins">plugin examples</a> and the <a href="#virtuallife-examples">VirtualLife Examples</a> for now!</p>
<h2 id="virtuallife-examples">VirtualLife Examples</h2>
<ul>
<li><a href="http://fopina.github.io/tgbot-priberambot">PriberamBot</a> - uses webhooks, inline queries, packaged for Heroku</li>
<li><a href="http://fopina.github.io/tgbot-buttiebot">ButtieBot</a> - uses webhooks, sends photos, packaged for OpenShift</li>
<li><a href="http://fopina.github.io/tgbot-euromillionsbot">EuromillionsBot</a> - uses webhooks, inline queries, packaged for OpenShift</li>
<li><a href="http://pmpfl.github.io/indieshufflebot">IndieShuffleBot</a> - uses webhooks, sends audio, packaged for OpenShift</li>
</ul>
