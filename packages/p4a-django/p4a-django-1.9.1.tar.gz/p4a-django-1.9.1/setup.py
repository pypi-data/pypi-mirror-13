import os
import sys
from distutils.sysconfig import get_python_lib

#from setuptools import find_packages, setup
from distutils.core import setup
#from pkgutil import walk_packages

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Django are
# still present in site-packages. See #18115.
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "django"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


EXCLUDE_FROM_PACKAGES = ['django.conf.project_template',
                         'django.conf.app_template',
                         'django.bin']


pkgs = ['django', 'django.views', 'django.dispatch', 'django.utils', 'django.conf', 'django.middleware', 'django.template', 'django.contrib', 'django.core', 'django.http', 'django.forms', 'django.test', 'django.templatetags', 'django.db', 'django.apps', 'django.views.decorators', 'django.views.generic', 'django.utils.translation', 'django.conf.locale', 'django.conf.urls', 'django.conf.app_template.migrations', 'django.conf.locale.lt', 'django.conf.locale.te', 'django.conf.locale.pt', 'django.conf.locale.bg', 'django.conf.locale.en_GB', 'django.conf.locale.sr', 'django.conf.locale.ml', 'django.conf.locale.sr_Latn', 'django.conf.locale.nn', 'django.conf.locale.ka', 'django.conf.locale.sv', 'django.conf.locale.mn', 'django.conf.locale.kn', 'django.conf.locale.ru', 'django.conf.locale.en', 'django.conf.locale.cs', 'django.conf.locale.en_AU', 'django.conf.locale.fr', 'django.conf.locale.de_CH', 'django.conf.locale.bn', 'django.conf.locale.sq', 'django.conf.locale.ar', 'django.conf.locale.id', 'django.conf.locale.ta', 'django.conf.locale.fi', 'django.conf.locale.es_NI', 'django.conf.locale.ko', 'django.conf.locale.da', 'django.conf.locale.es_MX', 'django.conf.locale.de', 'django.conf.locale.fa', 'django.conf.locale.eo', 'django.conf.locale.ca', 'django.conf.locale.es_AR', 'django.conf.locale.km', 'django.conf.locale.hr', 'django.conf.locale.az', 'django.conf.locale.es_CO', 'django.conf.locale.gl', 'django.conf.locale.ro', 'django.conf.locale.pl', 'django.conf.locale.he', 'django.conf.locale.eu', 'django.conf.locale.ga', 'django.conf.locale.sk', 'django.conf.locale.is', 'django.conf.locale.mk', 'django.conf.locale.zh_Hant', 'django.conf.locale.cy', 'django.conf.locale.es_PR', 'django.conf.locale.zh_Hans', 'django.conf.locale.th', 'django.conf.locale.hi', 'django.conf.locale.hu', 'django.conf.locale.it', 'django.conf.locale.ja', 'django.conf.locale.nl', 'django.conf.locale.gd', 'django.conf.locale.bs', 'django.conf.locale.nb', 'django.conf.locale.lv', 'django.conf.locale.el', 'django.conf.locale.sl', 'django.conf.locale.uk', 'django.conf.locale.tr', 'django.conf.locale.fy', 'django.conf.locale.et', 'django.conf.locale.pt_BR', 'django.conf.locale.es', 'django.conf.locale.vi', 'django.template.backends', 'django.template.loaders', 'django.contrib.webdesign', 'django.contrib.postgres', 'django.contrib.auth', 'django.contrib.sitemaps', 'django.contrib.admindocs', 'django.contrib.sites', 'django.contrib.contenttypes', 'django.contrib.gis', 'django.contrib.messages', 'django.contrib.redirects', 'django.contrib.staticfiles', 'django.contrib.syndication', 'django.contrib.sessions', 'django.contrib.flatpages', 'django.contrib.admin', 'django.contrib.humanize', 'django.contrib.webdesign.templatetags', 'django.contrib.postgres.fields', 'django.contrib.postgres.forms', 'django.contrib.postgres.aggregates', 'django.contrib.auth.tests', 'django.contrib.auth.migrations', 'django.contrib.auth.management', 'django.contrib.auth.handlers', 'django.contrib.auth.management.commands', 'django.contrib.sitemaps.management', 'django.contrib.sitemaps.management.commands', 'django.contrib.admindocs.tests', 'django.contrib.sites.migrations', 'django.contrib.contenttypes.migrations', 'django.contrib.gis.utils', 'django.contrib.gis.gdal', 'django.contrib.gis.geos', 'django.contrib.gis.sitemaps', 'django.contrib.gis.geoip', 'django.contrib.gis.maps', 'django.contrib.gis.geometry', 'django.contrib.gis.forms', 'django.contrib.gis.management', 'django.contrib.gis.serializers', 'django.contrib.gis.geoip2', 'django.contrib.gis.admin', 'django.contrib.gis.db', 'django.contrib.gis.gdal.raster', 'django.contrib.gis.gdal.prototypes', 'django.contrib.gis.geos.prototypes', 'django.contrib.gis.maps.google', 'django.contrib.gis.maps.openlayers', 'django.contrib.gis.geometry.backend', 'django.contrib.gis.management.commands', 'django.contrib.gis.db.backends', 'django.contrib.gis.db.models', 'django.contrib.gis.db.backends.postgis', 'django.contrib.gis.db.backends.spatialite', 'django.contrib.gis.db.backends.base', 'django.contrib.gis.db.backends.oracle', 'django.contrib.gis.db.backends.mysql', 'django.contrib.gis.db.models.sql', 'django.contrib.messages.storage', 'django.contrib.redirects.migrations', 'django.contrib.staticfiles.management', 'django.contrib.staticfiles.templatetags', 'django.contrib.staticfiles.management.commands', 'django.contrib.sessions.backends', 'django.contrib.sessions.migrations', 'django.contrib.sessions.management', 'django.contrib.sessions.management.commands', 'django.contrib.flatpages.migrations', 'django.contrib.flatpages.templatetags', 'django.contrib.admin.views', 'django.contrib.admin.migrations', 'django.contrib.admin.templatetags', 'django.contrib.humanize.templatetags', 'django.core.servers', 'django.core.checks', 'django.core.files', 'django.core.cache', 'django.core.mail', 'django.core.management', 'django.core.handlers', 'django.core.serializers', 'django.core.checks.compatibility', 'django.core.checks.security', 'django.core.cache.backends', 'django.core.mail.backends', 'django.core.management.commands', 'django.forms.extras', 'django.db.backends', 'django.db.migrations', 'django.db.models', 'django.db.backends.postgresql', 'django.db.backends.sqlite3', 'django.db.backends.base', 'django.db.backends.postgresql_psycopg2', 'django.db.backends.dummy', 'django.db.backends.oracle', 'django.db.backends.mysql', 'django.db.migrations.operations', 'django.db.models.fields', 'django.db.models.sql']


# Dynamically calculate the version based on django.VERSION.
version = __import__('django').get_version()


setup(
    name='p4a-django',
    version=version,
    url='http://www.djangoproject.com/',
    author='Django Software Foundation',
    author_email='foundation@djangoproject.com',
    description=('A high-level Python Web framework that encourages '
                 'rapid development and clean, pragmatic design.'),
    license='BSD',
    #packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    packages=pkgs,
    include_package_data=True,
    scripts=['django/bin/django-admin.py'],
    entry_points={'console_scripts': [
        'django-admin = django.core.management:execute_from_command_line',
    ]},
    extras_require={
        "bcrypt": ["bcrypt"],
    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


if overlay_warning:
    sys.stderr.write("""

========
WARNING!
========

You have just installed Django over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Django. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install Django.

""" % {"existing_path": existing_path})
