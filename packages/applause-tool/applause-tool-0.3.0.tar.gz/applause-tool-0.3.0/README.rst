Applause Tool
==============

Applause Tool is a command line package aimed at making it easy to connect
various continuous integration platforms with Applause Inc. services.


Setup
------


Prerequisities
--------------

Python
~~~~~~~
Applause Tool requires Python2.6+ interpreter to be installed on your
machine. If you are using Linux/Unix/MacOSX system this prerequisit is already met.
Please consult your platform specific Python installation scripts for more info.

PIP
~~~~
Python 2.7.9 and later (on the python2 series), and Python 3.4 and later include pip by default, so you may have pip already.
If not please consult this page for a ready to use recipe to install it on your local machine:
https://pip.pypa.io/en/latest/installing.html#install-pip


Installation
-------------


To install applause-tool, run:

.. code-block:: bash

    $ pip install applause-tool



To verify your installation please run the following command in your terminal:


.. code-block:: bash

    $ applause-tool --version



Updating
---------

To update applause-tool, run:

.. code-block:: bash

    $ pip install applause-tool --upgrade


Usage
======

Login
-----

Before running product specific commands you need to log in with your Applause Account.
In case you don't have one please consult you Applause project manager.


During the process you will be asked to provide your username and password. Please note that
the script will not store directly store your credentials. After successful login we do persist
generated OAuth tokens in the home directory of the currently logged in user. If you won't pass
the credentials inline, you will be prompted for them.

.. code-block:: bash

    $ applause-tool login
    # OR
    $ applause-tool login -u username -p password


Logout
-------

If you wish to remove the Applause Tool from your OS please make sure to log out from you existing
session. You can do that by typing:

.. code-block:: bash

    $ applause-tool logout


Account
--------

At any point in time you can check who is the actively logged in user by running:

.. code-block:: bash

    $ applause-tool account


Applause SDK
-------------

In order to upload & distribute your build please run the following command in your terminal:


.. code-block:: bash

    $ applause-tool sdk distribute COMPANY_ID APP_ID /path/to/build [-e john.smith@test.com -c "New Release"]


* COMPANY_ID - ID of the company you created in the Applause SDK service.
* APP_ID - ID of the application to which you wish to upload your builds to.
* PATH - A full path to the build you wish to upload
* (Optional) -e - emails to which you wish to distribute your build to. Please make sure to repeat this option for each email you wish to add.
* (Optional) -c - changelog to attach to the build file in Applause SDK. This operation will add more information on the build OTA (over-the-air) installation page connected to the distribution email.


**Example 1**

Simple distribution with email list & changelog comming directly from the command line:

.. code-block:: bash

    $ applause-tool sdk distribute 3 133 test_files/Test.ipa -e release@applause.com -c "Fresh new release, straight from the oven"

**Example 2**

Applause Tool allows you to provide both email & changelog information directly from locally created files.
In order to instruct Applause Tool to do so please add '@' sign at the start of the parameter value. For example:

.. code-block:: bash

    $ applause-tool sdk distribute 3 133 test_files/Test.ipa -e @/Users/john/files/AppDistributionList.txt -c "Fresh new release, straight from the oven"

Where the content of AppDistributionList.txt is as follows:

.. code-block::

    release@applause.com
    management@applause.com
    cannary@applause.com

Please note that emails are separated out with new line characters.

**Note**
You can obtain both COMPANY_ID and APP_ID values from you product specific URL address. The URL scheme is:

.. code-block::

    https://sdk.applause.com/companies/COMPANY_ID/application/APP_ID/dashboard/



.. code-block:: bash

    $ applause-tool sdk distribute COMPANY_ID APP_ID /path/to/build [-e john.smith@test.com -c @/home/user/builds/1.0/release-notes.txt]


Applause BETA
--------------

Currently only uploading build to Applause Mobile BETA Management is supported. Optionally changelog can be attached.

**Example**

Uploading build:

.. code-block::

    applause-tool beta upload 11 22 ~/my_apps/ExampleApp.ipa [-c @/home/user/builds/1.0/release-notes.txt]
    

Jenkins Integration
=====================


To integrate Applause Tool with Jenkins:

* Make sure that you have Python2.6+ and applause-tool installed on your job worker nodes
* We strongly recommend putting username and password for applause-tool logging in environment variables in worker node configuration
* Add an ``Execute shell`` build step in which you can invoke applause-tool as an ordinary shell command, like below:


.. code-block:: bash

    applause-tool login -u ${APPLAUSE_USER} -p ${APPLAUSE_PASSWORD}    
    applause-tool sdk distribute ...

* You can also install the Jenkins plugin PostBuildScript (https://wiki.jenkins-ci.org/display/JENKINS/PostBuildScript+Plugin) , which enables you
  to trigger those commands only if all the build steps are successfully completed.



Known issues
=====================

.. code-block:: bash

    InsecurePlatformWarning: A true SSLContext object is not available.


This has been widely discussed here: 
http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
We strongly recommend upgrading your Python version to 2.7.9 or higher.
