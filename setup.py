from setuptools import setup, find_packages

setup(
        name="nose_tddium",
        version="0.0.1",
        description="Output adapter for nosetests in Tddium",
        author="David Reiss",
        author_email="david@solanolabs.com",
        url="https://github.com/solanolabs/nose_tddium",
        platforms="Independent",
        install_requires = [
            "nose>=1.1.0",
            ],
        scripts=[],
        license="BSD",
        zip_safe=False,
        py_modules=['nose_tddium'],
        entry_points = {
            'nose.plugins.0.10': ['nose_tddium = nose_tddium:TddiumOutput'],
            },
        )
