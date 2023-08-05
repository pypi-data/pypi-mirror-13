from setuptools import setup, find_packages

setup(
        name = 'lquickplot',
        version = '0.0.3',
        keywords = ('simple', 'test'),
        description = 'just a simple test',
        license = 'MIT License',
        author = 'ap9035',
        author_email = 'ap9035@gmail.com',

        scripts = ['quickplot.py'],

        packages = find_packages(),
        platforms = 'any',
)
