{% extends "base.tpl" %}

{% block content %}

<section class="blocked">
    <h1><b>{{ record.details.name }}</b> has been blocked for your protection.</h1>
  <dl>
    <dt>Why was it blocked?</dt>
    <dd>{{ record.details.why|safe }}</dd>
    <dt>Who is affected?</dt>
    <dd>{{ record.details.who|safe }}</dd>
    <dt>What does this mean?</dt>
    <dd>
	  {% if record.severity and record.severity == 1 %}
      <p>
        Users are strongly encouraged to disable the problematic add-on or plugin,
        but may choose to continue using it if they accept the risks described.
      </p>
      {% else %}
      <p>
        The problematic add-on or plugin will be automatically disabled and no
        longer usable.
      </p>
      {% endif %}

    When Mozilla becomes aware of add-ons, plugins, or other third-party software that seriously compromises Firefox security, stability, or performance and meets <a href="http://wiki.mozilla.org/Blocklisting">certain criteria</a>, the software may be blocked from general use.  For more information, please read <a href="http://support.mozilla.org/kb/add-ons-cause-issues-are-on-blocklist">this support article</a>.</dd>
  </dl>
      <footer>
   {% if record.details.bug %}
    <footer>Blocked on {{ record.details.created|datetime }}. <a href="{{ record.details.bug }}">View block request</a>.</footer>
  {% else %}
    <footer>Blocked on {{ record.details.created|datetime }}.</footer>
  {% endif %}
  </section>

{% endblock %}
