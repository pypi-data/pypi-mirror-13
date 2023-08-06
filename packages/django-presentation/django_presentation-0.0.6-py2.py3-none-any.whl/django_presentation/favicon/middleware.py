from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.views.generic.base import RedirectView


class FaviconUrl(object):
    def process_template_response(self,request,response):
        response.context_data['faviconUrl']=static(settings.FAVICON_PATH)
        return response
