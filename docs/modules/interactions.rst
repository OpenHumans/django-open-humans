########################
Interacting with Members
########################

For each user that has logged in through their *Open Humans* account you will get
an object of the ``OpenHumansMember`` class, allowing you to interact with them through the
Open Humans API & platform. Below are some examples of how you can use this app to interact with
your Open Humans members.

More information can be found in the :ref:`model.py section <model-ref>`.


Accessing an ``OpenHumansMember`` object
========================================

Each ``OpenHumansMember`` object is associated with a regular *Django* ``User`` object. Through the Django shell this looks like this:

.. code-block:: Python
  :caption: ./manage.py shell
  :lineno-start: 13

  In [1]: from django.contrib.auth import get_user_model

  In [2]: User = get_user_model()

  In [3]: single_user = User.objects.all()[0] # get a single user

  In [4]: print(single_user.openhumansmember)
  <OpenHumansMember(oh_id='12341337')>

Due to this you can also easily access each ``OpenHumansMember`` inside your views from the
``request`` object:

.. code-block:: Python
  :caption: views.py

  def my_view(request):
    open_humans_member = request.user.openhumansmember


Accessing files for an ``OpenHumansMember`` object
==================================================

The ``OpenHumansMember`` objects have a class method to list and access the files for them:

.. code-block:: Python
  :caption: ./manage.py shell

  In [1]: from openhumans.models import OpenHumansMember

  In [2]: oh_member = OpenHumansMember.objects.all()[0]

  In [3]: print(oh_member.list_files())
  [{'id': 1234, 'basename': 'my_file.json', 'created': '2018-11-23T17:28:49.114250Z', 'download_url': 'https://example.com/my_file.json', 'metadata': {'tags': ['json', 'data', 'foo'], 'description': 'an example file'}, 'source': 'direct-sharing-1337'}]

The ``OpenHumansMember.list_files()`` function returns a list of dictionaries, containing metadata for the files available as well as the download link for each file.

Deleting files for an ``OpenHumansMember`` object
==================================================

The ``OpenHumansMember`` objects have two class methods to delete individual files or multiple files:
``OpenHumansMember.delete_all_files()`` and ``OpenHumansMember.delete_single_file()``.

**Warning: If you use the filename to decide which files to delete with the ``delete_single_file``
function it will delete all files with a given name if there is more than one!**

.. code-block:: Python
  :caption: ./manage.py shell

  In [1]: from openhumans.models import OpenHumansMember

  In [2]: oh_member = OpenHumansMember.objects.all()[0]

  ### Delete a single file by file-ID (see accessing files)

  In [3]: oh_member.delete_single_file(file_id=1234)

  ### Delete one or multiple files by file-name.

  In [4]: oh_member.delete_single_file(file_basename='my_file.json')

  ### Delete all files of a member

  In [5]: oh_member.delete_all_files()


Uploading files for an ``OpenHumansMember`` object
==================================================

To upload files you can use the ``OpenHumansMember.upload()`` function. For this you
will have to provide an open stream (text or binary), a file name that should be used and some meta data.


.. code-block:: Python
  :caption: views.py

  def upload_file(request):
    oh_member = request.user.openhumansmember

    with open('example_file.json', 'r') as f:
      oh_member.upload(
        f,
        'example.json',
        metadata = {'description': 'foo', 'tags': ['test', 'example']}
      )
