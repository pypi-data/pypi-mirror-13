# -*- coding: utf-8 -*-
"""widgets to be used in a form"""

from bs4 import BeautifulSoup

from django.forms import Media

from floppyforms.widgets import TextInput

from djaloha import settings


class AlohaInput(TextInput):
    """
    Text widget with aloha html editor
    requires floppyforms to be installed
    """

    template_name = 'djaloha/alohainput.html'

    def __init__(self, *args, **kwargs):
        # for compatibility with previous versions
        kwargs.pop('text_color_plugin', None)

        self.aloha_plugins = kwargs.pop('aloha_plugins', None)
        self.extra_aloha_plugins = kwargs.pop('extra_aloha_plugins', None)
        self.aloha_init_url = kwargs.pop('aloha_init_url', None)
        super(AlohaInput, self).__init__(*args, **kwargs)

    def _get_media(self):
        """
        return code for inserting required js and css files
        need aloha , plugins and initialization
        """

        try:
            aloha_init_url = self.aloha_init_url or settings.init_url()
            aloha_version = settings.aloha_version()

            aloha_plugins = self.aloha_plugins
            if not aloha_plugins:
                aloha_plugins = settings.plugins()

            if self.extra_aloha_plugins:
                aloha_plugins = tuple(aloha_plugins) + tuple(self.extra_aloha_plugins)

            css = {
                'all': (
                    "{0}/css/aloha.css".format(aloha_version),
                )
            }

            javascripts = []

            if not settings.skip_jquery():
                javascripts.append(settings.jquery_version())

            #if aloha_version.startswith('aloha.0.22.') or aloha_version.startswith('aloha.0.23.'):
            javascripts.append("{0}/lib/require.js".format(aloha_version))

            javascripts.append(aloha_init_url)
            javascripts.append(
                u'{0}/lib/aloha.js" data-aloha-plugins="{1}'.format(aloha_version, u",".join(aloha_plugins))
            )
            javascripts.append('djaloha/js/djaloha-init.js')
            
            return Media(css=css, js=javascripts)
        except Exception, msg:
            print '## AlohaInput._get_media Error ', msg

    media = property(_get_media)

    def value_from_datadict(self, data, files, name):
        """return value"""
        value = super(AlohaInput, self).value_from_datadict(data, files, name)
        return self.clean_value(value)

    def clean_value(self, origin_value):
        """This apply several fixes on the html"""
        return_value = origin_value
        if return_value:  # don't manage None values
            callbacks = (self._fix_br, self._fix_img, )
            for callback in callbacks:
                return_value = callback(return_value)
        return return_value

    def _fix_br(self, content):
        """
        This change the <br> tag into <br />
        in order to avoid empty lines at the end in  HTML4 for example for newsletters
        """
        return content.replace('<br>', '<br />')

    def _fix_img(self, content):
        """Remove the handlers generated on the image for resizing. It may be not removed by editor in some cases"""
        soup = BeautifulSoup(content, 'html.parser')

        wrapped_img = soup.select(".ui-wrapper img")
        if len(wrapped_img) > 0:
            img = wrapped_img[0]

            # Remove the ui-resizable class
            img_classes = img.get('class', None) or []
            img_classes.remove('ui-resizable')
            img['class'] = img_classes

            # Replace the ui-wrapper by the img
            wrapper = soup.select(".ui-wrapper")[0]
            wrapper.replace_with(img)

            content = unicode(soup)

        return content
