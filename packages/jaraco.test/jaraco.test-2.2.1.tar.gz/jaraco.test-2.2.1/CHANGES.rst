2.2
===

Moved hosting to Github.

2.1
===

Moved services module to ``jaraco.test.services`` and
``jaraco.mongodb.service``.

2.0.5
=====

Extend timeout for MongoDB mongod to listen on the port from
one second to three seconds, preventing spurious failures
on slower systems.

2.0.2
=====

Replace lingering reference to removed socket_test module.

2.0.1
=====

Fix issue in MongoDB finder where MONGODB_HOME wasn't honored.

2.0
===

Removed jaraco.test.socket_test. Use portend instead.

Use setuptools_scm for version generation.

1.9
===

Improved MongoDBFinder to locate MongoDB in new canonical
locations used by the MongoDB Windows Installer.
