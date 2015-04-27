Creating bundle
===============

    $ python setup.py sdist

Uploading bundle to PyPi
========================

    $ python setup.py sdist upload
    
    OR


    $ python setup.py sdist upload -r pypi

    This needs we have a ~/.pypi file. Its content should be like:-

[distutils] # this tells distutils what package indexes you can push to
index-servers =
    pypi
    pypitest #Optional

[pypi]
repository: https://pypi.python.org/pypi
username: <username>
password: <password>

[pypitest] #Optional
repository: https://testpypi.python.org/pypi
username: <username>
password: <password>
