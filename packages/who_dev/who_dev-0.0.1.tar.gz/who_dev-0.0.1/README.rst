who_dev
========

Testing Authenticataion for repoze.who v2 WSGI Applications

This plugin is intented for quickly configuring test users for
development purposes. Its use is not recommended in production systems.


Installing
----------

::

  pip install who_dev


Installing the mainline development branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The plugin is hosted in `a git branch hosted at github.com
<https://github.com/m-martinez/who_dev.git>`_. To get the latest source
code, run::

    git clone git@github.com:m-martinez/who_dev.git

Then run the command below::

    pip install -e who_dev/


Configuring ``repoze.who`` in a INI file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can configure your ``repoze.who`` based authentication via a ``*.ini`` file,
and then load such settings in your application.

Say we have a file called ``who.ini`` with the following contents::

    [general]
    request_classifier = repoze.who.classifiers:default_request_classifier
    challenge_decider = repoze.who.classifiers:default_challenge_decider

    [identifiers]
    plugins =
      auth_tkt

    [authenticators]
    plugins =
      auth_tkt
      dev_auth

    [challengers]
    plugins =
        form;browser

    [mdproviders]
    plugins =
      dev_properties
      dev_groups

    [plugin:form]
    use = repoze.who.plugins.form:make_plugin
    rememberer_name = auth_tkt

    [plugin:auth_tkt]
    use = repoze.who.plugins.auth_tkt:make_plugin
    secret = s3kr1t

    [plugin:dev_auth]
    use = who_dev:JSONAuthenticatorPlugin
    data = {
      "someuser":  {
        "password": "abc123",
        "properties": {
          "first_name": "Some",
          "last_name": "User",
          "email": "someuser@localhost"
        },
        "groups": ["members", "editors"]
      }
    }

    [plugin:dev_properties]
    use = who_dev:JSONPropertiesPlugin
    source_key = properties

    [plugin:dev_groups]
    use = who_dev:JSONPropertiesPlugin
    source_key = groups


Framework-specific documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may want to check the following framework-specific documents to learn tips
on how to implement `repoze.who` in the framework you are using:

 * **Pyramid**: `pyramid_who
   <http://docs.pylonsproject.org/projects/pyramid-who/en/latest>`_.
 * **Pylons**: `Authentication and Authorization with repoze.who
   <http://wiki.pylonshq.com/display/pylonscookbook/Authentication+and+Authorization+with+%60repoze.who%60>`_.
 * **TurboGears 2**: `Authentication and Authorization in TurboGears 2
   <http://www.turbogears.org/2.1/docs/main/Auth/index.html>`_
   (``repoze.who`` is the default authentication library).


Configuration
-------------

JSONAuthenticatorPlugin
~~~~~~~~~~~~~~~~~~~~~~~

This plugin uses a JSON object as a database, where each key in the object is
the userid and the value is another object with specific details about the user, which
can then be used along ith ``JSONPropertiesPlugin`` to retrieve specific details about
the user.

Each record for a user must at a minimum contain a ``password`` entry so that
the user can authenticate, for example:

::

  data={
    "someuser": {"password": "abc123"},
    "otheruser": {"password": "xyz789"}
  }


==================== ======= ========================================================
Setting              Default Description
==================== ======= ========================================================
``data``                      **Required** A JSON object contaiing records for each
                              test userid.
==================== ======= ========================================================


JSONPropertiesPlugin
~~~~~~~~~~~~~~~~~~~~

This plugin uses the specific key in the authenticator data to lookup
specific details about a user.

=================== =============== =======================================================
Setting             Default         Description
=================== =============== =======================================================
``source_key``                      **Required** Sets the remote user data to the value
                                    located at ``source_key`` for the currently
                                    authenticated userid.
=================== =============== =======================================================
