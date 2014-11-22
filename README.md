Pyramid Authorization and Authentication Demo with SQLAlchemy
=============================================================

This Demo is based on the "Object-Level Security"-part of http://michael.merickel.org/projects/pyramid_auth_demo/index.html

I've added basic SQLAlchemy support to the models and the views. There is a group-object in the database, but at the moment
it is not used.


Installation
------------

```bash
virtualenv env
cd env
git clone git://github.com/peletiah/pyramid_auth_demo_sqlalchemy.git auth_tut
cd auth_tut
../bin/python setup.py develop
../bin/pserve development.ini --reload
```

If everything looks fine, go to http://localhost:6543, else let me know!

Maintenance/Testing
-------------------


You can get an interactive python-shell where you can test the DB-model and other functions by issuing
```
../bin/python auth_tut/devtools/sqlalchemy_shell.py
```

