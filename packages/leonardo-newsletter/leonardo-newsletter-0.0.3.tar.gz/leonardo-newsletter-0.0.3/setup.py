import setuptools

# In python < 2.7.4, a lazy loading of package `pbr` will break
# setuptools if some other modules registered functions in `atexit`.
# solution from: http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing  # noqa
except ImportError:
    pass

setuptools.setup(
    setup_requires=['pbr'],
    pbr=True,
    dependency_links=['http://github.com/michaelkuty/emencia-django-newsletter/tarball/master#egg=emencia_django_newsletter-0.4'])
