rngslib: R interface for NGS data analysis

Prerequisites:

1. R 3.2+ (down to 3.0 probably OK). When compiling R from source, do not forget to specify –enable-R-shlib at the ./configure step.
2. Python 3.4, with intended compatibility with 2.7 and 3.3.
3. readline
4. rpy2

Install rpy2:

1. From source.
    > tar -xzf <rpy_package>.tar.gz
    > cd <rpy_package>
    > python setup.py build install
    or
    > python setup.py build --r-home /opt/packages/R/lib install # give explicitly the location for the R HOME

2. Binaries.
    Get details from http://rpy2.readthedocs.org/en/version_2.7.x/overview.html#background.


Install rngslib:

    > easy_install --prefix=$HOME/local rngslib
