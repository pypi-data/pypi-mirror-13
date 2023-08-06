docker-compose wrapper allowing for user data and env. var defaults
===================================================================

``dcw`` can be invoked with exactly the same commands as
docker-compose.  If ``-f``/``--file`` is specified as the first option
the filename to be read will be taken from there. Otherwise
``docker-compose.yml`` is assumed (currently the alternative default
files are not tested/read) the YAML file.

The YAML file has to be in the version: "2" format.

``dcw`` then processes the YAML file and invokes
``docker-compose --file=-`` and the original commandline arguments,
then pipes in the processed data (as YAML).

processing
==========

The following subsections describe the processing that ``dcw`` does
and the reasons for doing so.

reading defaults
----------------

The key value pairs under ``user-data -> env-defaults`` are taken
to populate ``os.environ``, unless the key already exists. This means 
you can set defaults for the environment variables used in the 
docker-compose YAML file.


stripping user-data
-------------------

Any existing top-level key "user-data" or starting with "user-data-" is
removed. This allows for storing additional data in the file 
(which would require yet another configuration file or extraction
from YAML comments).

Example
=======

This is the first part of one of my ``docker-compose.yml`` files::

  version: '2'
  user-data:
    author: Anthon van der Neut <a.van.der.neut@ruamel.eu>
    description: mongo container
    env-defaults:
      PORT: 587    # override during development
  services:
    submission:
      container_name: submission
      build: .
      ports:
      - ${PORT}:587


The "author" and "description" information can easily be extracted and
used by other processes.

While developing I cannot use the submission port (587) as that is
already taken, and there I do `export PORT=10587`. On my deployment machine
I don't want to have to set PORT to the default value. With ``dcw``
the PORT env. var is set to 587 because there is no environment var "PORT"
defined on that machine.




