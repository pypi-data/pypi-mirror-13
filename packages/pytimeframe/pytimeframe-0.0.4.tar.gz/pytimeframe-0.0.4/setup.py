'''
pytf setup script
'''

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


me = 'Abhinav Kotak'
memail = 'in.abhi9@gmail.com'


packages = ['pytimeframe']

setup (
    name='pytimeframe',
    version='0.0.4',
    zip_safe=True,
    description='Span date range from time frame string',
    author=me,
    author_email=memail,
    maintainer=me,
    maintainer_email=memail,
    install_requires=['pytz', 'arrow'],
    url='https://github.com/inabhi9/pytimeframe',
    keywords=['timeframe', 'datetime', 'time'],
    packages=packages,
    platforms=['Independant'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
