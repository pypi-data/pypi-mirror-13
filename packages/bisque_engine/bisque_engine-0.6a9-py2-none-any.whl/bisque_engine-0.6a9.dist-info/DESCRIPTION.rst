BisQue module engine
--------------------

Support execution of modules in bisque


Getting started:
::

     mkdir engine; cd engine;
     virtualenv bqenv; source bqenv/bin/activate
     pip install -U pip setuptools
     pip install bisque_engine
     bq-admin setup engine


Create your fist module:
::

    bq-admin create-module [python|matlab] mymodule
    bq-admin server start

Navigate http://localhost:6543/engine_service:




Register a module with an existing BisQue service:
::

   bq-admin module register -r http://bisque-host.org/ http://localhost:6543/engine_service/mymodule



See  http://bioimage.ucsb.edu/bisque




0.6
---

-  Initial version


