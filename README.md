Pyramid Authorization and Authentication Demo with SQLAlchemy
=============================================================

This Demo is based on the "Object-Level Security"-part of http://michael.merickel.org/projects/pyramid_auth_demo/index.html

I've added basic SQLAlchemy support to the models and the views.


Installation
------------

```bash
virtualenv env
cd env
git clone git://github.com/peletiah/pyramid_auth_demo_sqlalchemy.git auth_tut
cd auth_tut
../bin/python setup.py develop
../bin/pserve development.ini
```

If everything looks fine, go to http://localhost:6543, else let me know!
