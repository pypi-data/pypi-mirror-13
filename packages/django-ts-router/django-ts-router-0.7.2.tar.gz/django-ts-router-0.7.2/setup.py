# vim:fileencoding=utf-8

from setuptools import setup, find_packages

setup(name='django-ts-router',
      version='0.7.2',
      description='Generates a TypeScript (or JavaScript) source code that includes URL reverse functions '
                  'for your Django app.',
      url='https://github.com/strippers/django-ts-router',
      license='LGPL',
      author='Tomohiro Otsuka',
      author_email='t.otsuka@gmail.com',
      packages=find_packages(
          exclude=['*tests*', 'testproj']
      ),
      package_data={
          '': ['templates/**/*']
      },
      install_requires=[],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django :: 1.8',
          'Framework :: Django :: 1.9',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Internet :: WWW/HTTP',
      ],
      keywords=['django', 'javascript', 'typescript', 'routing', 'url'],
      )
