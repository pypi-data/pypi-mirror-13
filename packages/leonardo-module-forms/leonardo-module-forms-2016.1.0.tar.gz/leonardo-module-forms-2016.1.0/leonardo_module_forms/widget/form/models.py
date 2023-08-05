# -#- coding: utf-8 -#-

from crispy_forms.bootstrap import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from django.db import models
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from form_designer.models import FormContent
from leonardo.module.web.models import Widget
from leonardo.module.media.models import Folder, MEDIA_MODELS
from leonardo.module.media.utils import handle_uploaded_file
from django.conf import settings


def _handle_uploaded_file(f):
    '''internal wrapper
    '''
    return handle_uploaded_file(f, folder=settings.FORM_FILES_DIRECTORY,
                                is_public=settings.FORM_FILES_PRIVATE)


class FormWidget(Widget, FormContent):

    form_layout = models.TextField(
        _('Form Layout'), blank=True, null=True,
        help_text=_('Crispy Form Layout see \
            http://django-crispy-forms.readthedocs.org/en/latest/layouts.html'))

    class Meta:
        abstract = True
        verbose_name = _('form')
        verbose_name_plural = _('forms')

    def process_valid_form(self, request, form_instance, **kwargs):
        """ Process form and return response (hook method). """
        return render_to_string(self.template, context)

    def handle_files(self, form_instance, request):
        '''handle files from request'''

        files = []
        for key in request.FILES.keys():
            saved_file = _handle_uploaded_file(request.FILES[key])
            _key = key.replace(self.prefix + '-', '')
            form_instance.cleaned_data[_key] = '%s - %s' % (
                str(saved_file), saved_file.url)
            files.append(saved_file)
        return files

    @property
    def prefix(self):
        return 'fc%d' % self.id

    def render(self, request, **kwargs):
        context = RequestContext(
            request, {'widget': self})

        form_class = self.form.form()

        formcontent = request.POST.get('_formcontent')

        if request.method == 'POST' and (
                not formcontent or formcontent == smart_text(self.id)):
            form_instance = form_class(
                request.POST, request.FILES, prefix=self.prefix)

            if form_instance.is_valid():

                # handle files
                files = self.handle_files(form_instance, request)

                process_result = self.form.process(form_instance, request)

                # add reverse reference to files
                for file in files:
                    file.description = process_result['save_fs'].formatted_data()
                    file.save()

                context = RequestContext(
                    request,
                    {
                        'widget': self,
                        'message': self.success_message or process_result or u'',
                    }
                )
            else:
                context["form"] = form_instance

        else:
            form_instance = form_class(prefix=self.prefix)

            # use crispy forms
            form_instance.helper = FormHelper(form_instance)
            form_instance.helper.form_action = '#form{}'.format(self.id)

            if self.form_layout:

                try:
                    form_instance.helper.layout = eval(self.form_layout)
                except Exception as e:
                    raise e

            else:
                # use default layout
                if self.show_form_title:
                    form_instance.helper.layout = Layout(
                        Fieldset(self.form.title),
                    )
                else:
                    form_instance.helper.layout = Layout()

                # Moving field labels into placeholders
                layout = form_instance.helper.layout
                for field_name, field in form_instance.fields.items():
                    layout.append(Field(field_name, placeholder=field.label))

                form_instance.helper.layout.extend([ButtonHolder(
                    Submit('submit', 'Submit', css_class='button white')
                )
                ])

                # still have choice to render field labels
                if not self.show_form_title:
                    form_instance.helper.form_show_labels = False

            context['form'] = form_instance

        return render_to_string(self.get_template_name(), context)
