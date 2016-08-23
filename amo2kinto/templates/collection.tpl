{% extends "base.tpl" %}

{% block content %}
<section class="blocked">
<hgroup>
  <h1>Blocked Add-ons</h1>
  <h2>The following software is known to cause serious security, stability, or performance issues with Firefox.</h2>
</hgroup>


<ul id="blocked-items">
{% for record in records %}
  <li><span class="dt">{{ record.details.created|datetime }}</span>: <a href="{{ record.get('blockID', record['id']) }}.html">{{ record.details.name }}</a></li>
{% endfor %}
</ul>

</section>
{% endblock %}

