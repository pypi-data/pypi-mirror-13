django-staticfiles-dotd
=======================


    STATICFILES_FINDERS = (
        'staticfiles_dotd.finders.DotDFinder',
         'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )


Doesn't work with ``collectstatic [..] --link``.
