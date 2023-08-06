#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.translations import translations
from woost.models import Extension, Configuration

translations.define("GoogleAnalyticsExtension",
    ca = u"Google Analytics",
    es = u"Google Analytics",
    en = u"Google Analytics"
)

translations.define("GoogleAnalyticsExtension-plural",
    ca = u"Google Analytics",
    es = u"Google Analytics",
    en = u"Google Analytics"
)

translations.define("GoogleAnalyticsExtension.account",
    ca = u"Compte",
    es = u"Cuenta",
    en = u"Account"
)


class GoogleAnalyticsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Integra el lloc web amb Google Analytics.""",
            "ca"
        )
        self.set("description",
            u"""Integra el sitio web con Google Analytics.""",
            "es"
        )
        self.set("description",
            u"""Integrates the site with Google Analytics.""",
            "en"
        )

    def _load(self):

        from woost.extensions.googleanalytics import (
            strings,
            configuration,
            website,
            document,
            eventredirection
        )

        from cocktail.events import when
        from woost.controllers import CMSController

        @when(CMSController.producing_output)
        def handle_producing_output(e):
            publishable = e.output.get("publishable")
            if (
                publishable is None
                or getattr(publishable, "is_ga_tracking_enabled", lambda: True)()
            ):
                html = e.output.get("head_end_html", "")
                if html:
                    html += " "
                html += self.get_analytics_script()
                e.output["head_end_html"] = html

    def get_analytics_script(self):
        config = Configuration.instance
        account = config.get_setting("google_analytics_account")
        return """
        <script type="text/javascript">
            var _gaq = _gaq || [];
            _gaq.push(['_setAccount', '%s']);
            _gaq.push(['_trackPageview']);
            (function() {
            var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
            ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
            var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
            })();
        </script>""" % account

