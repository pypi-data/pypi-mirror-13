
from feincms_oembed.contents import FeedContent
from django.utils.translation import ugettext_lazy as _

from leonardo.module.web.models import Widget
from django.template.loader import render_to_string


class FeedWidget(Widget, FeedContent):

    def render_content(self, options):

        return render_to_string(
            self.get_template, {
                'feed': self.feed, 'widget': self,
                'request': options.get('request')
                })

    class Meta:
        abstract = True
        verbose_name = _('RSS Feed')
        verbose_name_plural = _('RSS Feeds')
