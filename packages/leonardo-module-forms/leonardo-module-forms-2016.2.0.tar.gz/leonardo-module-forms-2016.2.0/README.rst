
==============
Leonardo Forms
==============

Form builder for Leonardo.

Technicaly is only FeinCMS `Form Designer`_ and `Remote Forms`_.

Visit `Demo Site`_

.. contents::
    :local:

Installation
------------

.. code-block:: bash

    pip install leonardo_module_forms

or as leonardo bundle

.. code-block:: bash

    pip install django-leonardo["forms"]

Optionaly you can install remote forms typing this

.. code-block:: bash

    pip install leonardo_module_forms[remote]

https://github.com/WiserTogether/django-remote-forms

and google recaptcha

.. code-block:: bash

    pip install leonardo_module_forms[recaptcha]

Add ``leonardo_module_forms`` to APPS list, in the ``local_settings.py``::

    APPS = [
        ...
        'forms'
        ...
    ]

Load new template to db

.. code-block:: bash

    python manage.py sync_all

Writing your own Layout
-----------------------

For customization is there two options.
One is defining Crispy Layout as you can see below

.. code-block:: python

    Layout(
        Fieldset(
            'first arg is the legend of the fieldset',
            'test',
        ),
        ButtonHolder(
            Submit('submit', 'Submit', css_class='button white')
        ),
        HTML("""
            <p>We use notes to get better, <strong>please help us {{ username }}</strong></p>
        """),
    )

for full reference visit http://django-crispy-forms.readthedocs.org/en/latest/layouts.html

Second is writing your custom template and render form field by field. For this is there template.

See `Leonardo`_

.. _`Demo Site`: http://demo.cms.robotice.cz
.. _`Leonardo`: https://github.com/django-leonardo/django-leonardo
.. _`Form Designer`: https://github.com/antiflu/form_designer
.. _`Remote Forms`: https://github.com/WiserTogether/django-remote-forms
