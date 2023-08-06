Perform operations against Taskcluster API.
===========================================================================

Installation
------------

- ``virtual venv``
- ``source venv/bin/activate``
- ``pip install tctalker``

Configs specification
---------------------

Configs can be served in two ways:

- *via json config file* (check config.json.sample included within this repo)
- *via env vars*: **TASKCLUSTER_CLIENT_ID**, **TASKCLUSTER_ACCESS_TOKEN**, **TASKCLUSTER_CERTIFICATE**

Usage
-----

Usage example following Pypi installation:

- ``tctalker --verbose --conf config.json report_completed $taskid1 $taskid2 [...]``
- ``tctalker --conf config.json cancel $taskid3``
- ``tctalker rerun $taskid4`` *(assuming env vars coexist)*

