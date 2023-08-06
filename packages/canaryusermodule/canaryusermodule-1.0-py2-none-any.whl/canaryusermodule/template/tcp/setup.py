from setuptools import setup

setup(
    name='{{ pkgname }}',
    version='1.0',
    author='user',
    author_email='user@example.com',
    description='{{ description }}',
    url='https://canary.tools',
    # package a single python file
    py_modules=['{{ name }}'],
    # alternatively, package entire module (subdirectories)
    # packages=['{{ name }}'],
    zip_safe=False,
    include_package_data=True,
    entry_points={
        'canary.usermodule': [
            'example = {{ name }}:{{ pkgname }}'
        ]
    },
    platforms='any'
)
