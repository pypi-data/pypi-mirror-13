.. image:: https://gitlab.com/mayan-edms/document_renaming/raw/master/contrib/art/logo.png

Description
-----------
Mayan EDMS app to allow automatic renaming of documents upon upload.

License
-------
This project is open sourced under the `MIT License`_.

.. _`MIT License`: https://gitlab.com/mayan-edms/document_renaming/raw/master/LICENSE

Installation
------------
- Activate the virtualenv where you installed Mayan EDMS.
- Install from PyPI::

    pip install mayan-document_renaming

In your settings/local.py file add `document_renaming` to your `INSTALLED_APPS` list::

    INSTALLED_APPS += (
        'document_renaming',
    )

Run the migrations for the app::

    mayan-edms.py migrate


Usage
-----
- Create a sequence.
- Create a renaming template a document type using Django's templating language and referencing a sequence's `.next_value` method.

Example::

    Invoice-{{ sequence_invoice.next_value|stringformat:"05d" }}

This will rename a new document as "Invoice-0000". A subsequent document will be renamed as "Invoice-0001" and so on.


Development
-----------
Clone repository in a directory outside of Mayan EDMS::

    git clone https://gitlab.com/mayan-edms/document_renaming.git

Symlink the app into your Mayan EDMS' app folder::

    ln -s <repository directory>/document_renaming/ <Mayan EDMS directory>/mayan/apps

In your settings/local.py file add `document_renaming` to your `INSTALLED_APPS` list::

    INSTALLED_APPS += (
        'document_renaming',
    )

Run the migrations for the app::

    ./manage.py migrate
