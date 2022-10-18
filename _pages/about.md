---
permalink: /
title: "Welcom to Miaohui's Personal Homepage"
excerpt: "About me"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---
{% include base_path %}


Publications
======
  <ul>{% for post in site.publications %}
    {% include archive-single-cv.html %}
  {% endfor %}</ul>
  
Experiences
======
  <ul>
  {% for post in site.experience %}
  {% include archive-single.html %}
{% endfor %}
  </ul>


