from setuptools import setup


def readme():
    with open('README.rst', 'r') as f:
        content = f.read()
    return content


setup(name='django-neon',
      version='1.0.0',
      description='A CMS-Application for django-projects.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
      ],
      keywords='django cms-application',
      url='http://www.example.com',
      author='Klaus Bremer',
      author_email='bremer@bremer-media.de',
      license='MIT',
      packages=[
        'django_neon',
        'django_neon/migrations',
        'django_neon/models',
        'django_neon/processing',
        'django_neon/test',
      ],
      zip_safe=False
)
