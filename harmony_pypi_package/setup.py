import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='harmonydata',
    author='Thomas Wood',
    author_email='thomas@fastdatascience.com',
    description='Harmony Tool for Retrospective Data Harmonisation',
    keywords='harmony, harmonisation, harmonization, harmonise, harmonize',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/harmonydata/harmony',
    project_urls={
        'Documentation': 'https://harmonydata.org/',
        'Bug Reports':
        'https://github.com/harmonydata/harmony/issues',
        'Source Code': 'https://github.com/harmonydata/harmony',
        # 'Funding': '',
        # 'Say Thanks!': '',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=['pydantic==1.10.7','pandas==2.0.0','tika==2.6.0','lxml==4.9.2','langdetect==1.0.9','XlsxWriter==3.0.9','openpyxl==3.1.2','spacy==3.5.3'],
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    # entry_points={
    #     'console_scripts': [  # This can provide executable scripts
    #         'run=examplepy:main',
    # You can execute `run` in bash to run `main()` in src/examplepy/__init__.py
    #     ],
    # },
)
