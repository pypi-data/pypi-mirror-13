"""
iron: the powerful but simple build tool using flows.
"""
from setuptools import setup, find_packages


setup(
    name='iron',
    version='0.2.2',
    url='https://github.com/nvie/iron',
    license='BSD',
    author='Vincent Driessen',
    author_email='me@nvie.com',
    description=__doc__.strip(),
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=['click', 'more_itertools', 'humanize'],
    entry_points={
        'console_scripts': [
            'iron = iron.cli:cli',
        ],
    },
    extras_require={
        'all': ['jinja2', 'watchdog', 'htmlmin'],
        'html': ['htmlmin'],
        'watch': ['watch'],
        'jinja2': ['jinja2'],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
