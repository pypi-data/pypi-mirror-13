from setuptools import setup, find_packages

setup(
    name = 'django-classic-theme',
    version = __import__('classic_theme').__version__,
    description = 'The classic theme of the Django admin interface',
    long_description = 'This is the classic theme of the Django admin interface, copied from the master branch of Django before the flat theme replaced it.',
    url = 'https://github.com/vedantlath/django-classic-theme',
    author = 'Vedant Lath',
    author_email = 'vedant@lathconsultants.com',
    license = 'BSD',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
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
        'Topic :: Software Development :: User Interfaces'
    ],
    keywords = ['django', 'admin', 'theme', 'interface'],
    packages = find_packages(),
    include_package_data = True,
)
