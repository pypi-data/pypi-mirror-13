from setuptools import setup, find_packages
import avrsim

setup(
    name = avrsim.__name__,
    version = avrsim.__version__,
    description = avrsim.__summary__,
    url = avrsim.__url__,
    author = avrsim.__author__,
    author_email = avrsim.__email__,
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
    ]
)
