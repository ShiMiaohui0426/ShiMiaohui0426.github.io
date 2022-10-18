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

I am a student come from China. Now, I study as a Graduate Student in Waseda University supervised by Professor.Iwata in Dept. of Mordern ENgineering.
My research topic is about control, VR, Multi-Presence.

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


