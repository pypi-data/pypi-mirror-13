from setuptools import setup, find_packages


def get_long_description():
    with open('README.md', 'rb') as f:
        return f.read()


setup(
        name='django-news-page',
        version='0.1.0',
        packages=find_packages(),
        install_requires=[
            'django>=1.8',
        ],
        url='https://bitbucket.org/propp/django-news',
        license='MIT',
        author='Dmitry Sobolev',
        author_email='propp.ds@gmail.com',
        description='Simple news applications inspired by django-easy-news',
        long_description=get_long_description(),
        include_package_data=True,
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Framework :: Django',
            'Framework :: Django :: 1.8',
            'Framework :: Django :: 1.9',
            'Natural Language :: English',
            'Programming Language :: Python :: 2',
        ],
)
