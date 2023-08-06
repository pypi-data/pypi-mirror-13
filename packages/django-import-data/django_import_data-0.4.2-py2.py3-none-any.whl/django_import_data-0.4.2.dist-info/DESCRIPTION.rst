Django import data
==================

**Django import data** is a command-line tool for importing XML, HTML or
JSON data to django models via XSLT mapping.

Source code is located here -
https://github.com/lev-veshnyakov/django-import-data.

Basic features
--------------

Django import data can take any XML, HTML or JSON source file or URL as
an input and save entities from it to the django models without need to
modify an existing code.

It also supports saving of a related data in form one-to-many and
many-to-many.

Dependencies
------------

It uses `lxml <http://lxml.de>`__ library for all XML manipulations and
`dicttoxml <https://github.com/quandyfactory/dicttoxml>`__ library for
the transformation from JSON to XML.

Installation
------------

First you need to install dependencies for lxml library:

.. code:: bash

    sudo apt-get install libxml2-dev libxslt-dev python-dev

Then install django-import-data using pip:

.. code:: bash

    pip install django-import-data

If you want the latest version you can install it from Github:

.. code:: bash

    pip install git+https://github.com/lev-veshnyakov/django-import-data

Add import\_data to INSTALLED\_APPS:

.. code:: python

    INSTALLED_APPS = [
        ...
        'import_data',
    ]

Usage
-----

**Django import data** is a management command-line tool, that can be
used from the code as well.

Too see the list of console commands type:

.. code:: bash

    python manage.py help

In the output you will find import\_data section like below:

.. code:: bash

    [import_data]
        process_xslt
        validate_xml

To get help for the particular command type:

.. code:: bash

    python manage.py help process_xslt

.. code:: bash

    python manage.py help validate_xml

.. code:: bash

    python manage.py help json_to_xml

To call console commands from your code use
`django.core.management.call\_command <https://docs.djangoproject.com/es/1.9/ref/django-admin/#running-management-commands-from-your-code>`__:

.. code:: python

    from django.core.management import call_command

    call_command('process_xslt', 'http://stackoverflow.com/', 'transform.xslt', '--save')

How it works
------------

In a few words it takes a source in either XML or HTML, then takes
provided by you XSLT file, transforms the source into the specific XML
representation, and then saves the data from this XML to the database
using models.

The point is, that you don't need to write procedural code for saving
data. You only need to write XSLT files, which is actually XML. One file
for one source. By the source I mean a range of XML or HTML files in the
same format. For example all google search result pages have one schema.
That means that you can write only one XSLT transformation file to
import all search pages data.

The difficult moment is that you have to be familiar with XSLT and
Xpath.

XSLT and XPath
~~~~~~~~~~~~~~

XSLT is a language for transforming XML documents into XHTML documents
or to other XML documents.

XSLT uses XPath to find information in an XML document. XPath is used to
navigate through elements and attributes in XML documents.

If you are not familiar with that I reccomend you to read a `short
tutorial on
www.w3school.com <http://www.w3schools.com/xsl/xsl_intro.asp>`__.

Moreover, you have to know what an XML Schema is and a particular schema
language RELAX NG.

XML Schema and RELAX NG
~~~~~~~~~~~~~~~~~~~~~~~

**Django import data** uses RELAX NG to validate resuls of
transformations. That means if you write XSLT file wrong, it wouldn't be
accepted.

But you dont have to write RELAX NG schema yoursef, it's already
`included in the
module <https://github.com/lev-veshnyakov/django-import-data/tree/master/import_data/schema.rng>`__.

Resulting XML
~~~~~~~~~~~~~

After XSLT transformation and schema validation the resulting XML file
should be like following:

.. code:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <mapping>
        <model model="app.Author">
            <item key="1">
                <field name="name">Andrew Tanenbaum</field>
            </item>
            <item key="2">
                <field name="name">Donald Knuth</field>
            </item>
        </model>
        <model model="app.Book">
            <item key="1">
                <field name="name">Computer Networks</field>
                <field name="ISBN">0130661023</field>
                <fk model="app.Author" key="1"/>
            </item>
            <item key="2">
                <field name="name">The Art of Computer Programming</field>
                <field name="ISBN">0321751043</field>
                <m2mk model="app.Author" key="2"/>
            </item>
        </model>
    </mapping>

This XML can be automatically saved to the models.

It contains the root element ``<mapping/>``. Into it are nested
``<model/>`` elements. Each model element represents a particular django
model. You must provide ``model=""`` attributes, in which specify a
related model. Path to the model is in following format:
application\_name.ModelName, the same format like ``manage.py dumpdata``
uses.

Model elements don't have to be unique. If you specify several model
elements with the same model attribute, they will be merged together.
This concerns to item elements as well.

Model elements contain ``<item/>`` elements, representing particular
records in the database. They have only one required attribute
``name=""``, which sets the name of a related model field.

Foreign keys
~~~~~~~~~~~~

**Django import data** supports import of related entities in the form
one-to-many and many-to-many. To save such entities your models should
have appropriate foreign keys.

In a resulting XML you can use ``<fk/>`` and ``<m2m/>`` elements (see
above). They have ``model=""`` and ``key=""`` attributes, pointing to
the related ``<item/>`` elements.

Setting key attribute
~~~~~~~~~~~~~~~~~~~~~

The ``key=""`` attribute of ``<item/>`` elements must be unique by each
unique record. It has not to be the same as a primary key value in the
database. It even will not be stored (if you want to store a primary key
value, use ``<field/>`` element).

Therefore, the value of the ``key=""`` attribute not obliged to be
integer. You can use any sring. Often it's convenient to use an URL as
the key.

You can even omit filling that attribute if you don't have related
items.

**But one case is special**. That's when you don't have any unique
attributes in the source. In that case you can use ``generate-id(..)``
XPath function. It will generate unique IDs for every separate XML node
in the source.

Using JSON sources
~~~~~~~~~~~~~~~~~~

It's possible to use JSON sources. Because the transformation is
XSLT-based, JSON is converted to the appropriate XML.

For example the following JSON code:

.. code:: javascript

    {
      "firstName": "John",
      "lastName": "Smith",
      "age": 25,
      "address": {
        "streetAddress": "21 2nd Street",
        "city": "New York",
        "state": "NY",
        "postalCode": "10021"
      },
      "phoneNumber": [
        {
          "type": "home",
          "number": "212 555-1234"
        },
        {
          "type": "fax",
          "number": "646 555-4567"
        }
      ],
      "gender": {
        "type": "male"
      }
    }

will be converted to this XML:

.. code:: xml

    <?xml version="1.0" encoding=""?>
    <root>
      <firstName type="str">John</firstName>
      <lastName type="str">Smith</lastName>
      <age type="int">25</age>
      <address type="dict">
        <postalCode type="str">10021</postalCode>
        <city type="str">New York</city>
        <streetAddress type="str">21 2nd Street</streetAddress>
        <state type="str">NY</state>
      </address>
      <phoneNumber type="list">
        <item type="dict">
          <type type="str">home</type>
          <number type="str">212 555-1234</number>
        </item>
        <item type="dict">
          <type type="str">fax</type>
          <number type="str">646 555-4567</number>
        </item>
      </phoneNumber>
      <gender type="dict">
        <type type="str">male</type>
      </gender>
    </root>

That XML is supposed to be used for writing an XSLT transformation.

If you use some JSON source and want to find out which XML is related
for it, then use the command:

.. code:: bash

    python manage.py json_to_xml <URL>

After writing an XSLT transformation file you can use ``process_xslt``
specifying the URL of the JSON source.

JSON to XML transformations is performed by dicttoxml library written by
Ryan McGreal https://github.com/quandyfactory/dicttoxml.

Examples
--------

Save data to one model
~~~~~~~~~~~~~~~~~~~~~~

In this simple example we will parse the main page of
`stackoverflow.com <http://stackoverflow.com/>`__ and save titles of
recent questions to this model:

.. code:: python

    from django.db import models

    class Question(models.Model):
        title = models.CharField(max_length=255)

First we need to write an XSLT file:

.. code:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <mapping xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <model model="test_app.Question">
            <xsl:for-each select="//a[@class='question-hyperlink']">
                <item key="">
                    <field name="title">
                        <xsl:value-of select="."/>
                    </field>
                </item>
            </xsl:for-each>
        </model>
    </mapping>

Name it transform.xslt and perform the following command:

.. code:: bash

    python manage.py process_xslt http://stackoverflow.com/questions transform.xslt --validate

The output will be like this (but longer):

.. code:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <mapping>
      <model model="xml_json_import.Article">
        <item key="">
          <field name="title">customizing soap response attribute format</field>
        </item>
        <item key="">
          <field name="title">Second fragment loaded but not visible on screen</field>
        </item>
        <item key="">
          <field name="title">django-oscar :first time use "python manage.py migrate" gets error</field>
        </item>
        <item key="">
          <field name="title">JTable fireTableDataChanged() method doesn't refresh table</field>
        </item>
        <item key="">
          <field name="title">why the dynamic nodes dont respond to click in jstree?</field>
        </item>
        <item key="">
          <field name="title">Connecting kdb+ to R</field>
        </item>
      </model>
    </mapping>

Parameter ``--validate`` adds to output ``Document is valid``.

To save the result add the parameter ``--save`` to the command above.

Save data to related models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the same source and add two other models with foreign keys:

.. code:: python

    class Question(models.Model):
        title = models.CharField(max_length=255)
        user = models.ForeignKey('User', null=True)
        tags = models.ManyToManyField('Tag')

    class Tag(models.Model):
        title = models.CharField(max_length=255)

    class User(models.Model):
        title = models.CharField(max_length=255)

The XSLT file will be like following:

.. code:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <mapping xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
        <model model="test_app.Question">
            <xsl:for-each select="//div[@class='question-summary narrow']">
                <item key="">
                    <field name="title">
                        <xsl:value-of select=".//a[@class='question-hyperlink']"/>
                    </field>
                    <fk model="test_app.User">
                        <xsl:attribute name="key">
                            <xsl:value-of select="generate-id(.//div[@class='started']/a[2])"/>
                        </xsl:attribute>
                    </fk>
                    <xsl:for-each select=".//a[@class='post-tag']">
                        <m2mk model="test_app.Tag">
                            <xsl:attribute name="key">
                                <xsl:value-of select="generate-id(.)"/>
                            </xsl:attribute>
                        </m2mk>
                    </xsl:for-each>
                </item>
            </xsl:for-each>
        </model>

        <model model="test_app.Tag">
            <xsl:for-each select="//a[@class='post-tag']">
                <item>
                    <xsl:attribute name="key">
                        <xsl:value-of select="generate-id(.)"/>
                    </xsl:attribute>
                    <field name="title">
                        <xsl:value-of select="."/>
                    </field>
                </item>
            </xsl:for-each>
        </model>

        <model model="test_app.User">
            <xsl:for-each select="//div[@class='started']/a[2]">
                <item>
                    <xsl:attribute name="key">
                        <xsl:value-of select="generate-id(.)"/>
                    </xsl:attribute>
                    <field name="title">
                        <xsl:value-of select="."/>
                    </field>
                </item>
            </xsl:for-each>
        </model>
    </mapping>

Take notice how calculated attributes are set and how to use generate-id
function. In tis example we use both types of relationship: one-to-many
and many-to-many. This means that one question can have several tags,
but only one related user (which has changed the question last).

The output will be like following (but essential longer):

.. code:: xml

    <?xml version="1.0" encoding="utf-8"?>
    <mapping>
      <model model="test_app.Question">
        <item key="">
          <field name="title">C TCP Server doesn't send data before closing</field>
          <fk model="test_app.User" key="idp1407668180"/>
          <m2mk model="test_app.Tag" key="idp1407657924"/>
          <m2mk model="test_app.Tag" key="idp1407659948"/>
          <m2mk model="test_app.Tag" key="idp1407660732"/>
          <m2mk model="test_app.Tag" key="idp1407661540"/>
        </item>
        <item key="">
          <field name="title">Ninject Factory Extension</field>
          <fk model="test_app.User" key="idp1407665492"/>
          <m2mk model="test_app.Tag" key="idp1407676788"/>
          <m2mk model="test_app.Tag" key="idp1407674900"/>
          <m2mk model="test_app.Tag" key="idp1407678572"/>
          <m2mk model="test_app.Tag" key="idp1407678508"/>
          <m2mk model="test_app.Tag" key="idp1407652988"/>
        </item>
      <model model="test_app.Tag">
        <item key="idp1407657924">
          <field name="title">c</field>
        </item>
        <item key="idp1407659948">
          <field name="title">linux</field>
        </item>
        <item key="idp1407660732">
          <field name="title">sockets</field>
        </item>
        <item key="idp1407661540">
          <field name="title">tcp</field>
        </item>
        <item key="idp1407676788">
          <field name="title">c#</field>
        </item>
        <item key="idp1407674900">
          <field name="title">dependency-injection</field>
        </item>
        <item key="idp1407678572">
          <field name="title">ninject</field>
        </item>
        <item key="idp1407678508">
          <field name="title">ninject.web.mvc</field>
        </item>
        <item key="idp1407652988">
          <field name="title">ninject-extensions</field>
        </item>
      </model>
      <model model="test_app.User">
        <item key="idp1407668180">
          <field name="title">user3809727</field>
        </item>
        <item key="idp1407665492">
          <field name="title">user2119597</field>
        </item>
      </model>
    </mapping>



