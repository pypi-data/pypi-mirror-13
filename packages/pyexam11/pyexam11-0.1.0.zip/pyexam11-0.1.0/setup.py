from distutils.core import setup

setup(
    name = 'pyexam11',
    version = '0.1.0',
    description = 'A Python package example',
    author = 'Rajeev69',
    author_email = 'rajev.r@roanuz.com',
    url = 'https://github.com/Rajeev69/pyexam', 
    py_modules=['pyexam11'],
    install_requires=[
        # list of this package dependencies
    ],
    entry_points='''
        [console_scripts]
        pyexam11=pyexam11:exam1
    ''',
)