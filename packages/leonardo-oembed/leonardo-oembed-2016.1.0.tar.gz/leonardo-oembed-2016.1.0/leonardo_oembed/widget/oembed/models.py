
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from feincms_oembed.contents import OembedMixin
from feincms_oembed.models import CachedLookup
from leonardo.module.web.models import Widget

OEMBED_PARAMS = {
    'wmode': 'transparent',
}


class OembedWidget(OembedMixin, Widget):

    @classmethod
    def initialize_type(cls, OEMBED_PARAMS=OEMBED_PARAMS):
        cls._params = OEMBED_PARAMS

    def process(self, request, **kwargs):
        pass

    def render_content(self, options):
        params = {
            'type': 'default',
            'key': settings.EMBEDLY_KEY
            }
        params.update(self._params)

        try:
            embed = CachedLookup.objects.oembed(self.url, **params)
        except TypeError:
            raise ValidationError(
                _('I don\'t know how to embed %s.') % self.url)

        return render_to_string(
            self.get_template, {
                'content': embed, 'widget': self,
                'request': options.get('request')
                })

    class Meta:
        abstract = True
        verbose_name = _('External content')
        verbose_name_plural = _('External contents')
