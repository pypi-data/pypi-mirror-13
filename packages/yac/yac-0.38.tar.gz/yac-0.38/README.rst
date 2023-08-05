Your Atlassian Cloud
====================

There is a lot to love about the Atlassian Cloud versions of your
favorite Atlassian products, including:

-  fast provisioning
-  pain-free upgrades,
-  connect plugins,
-  all the bene's of sas

But their offering comes with constraints, including

-  no support for directory integration,
-  no support for type II plugins,
-  poor performance for large user bases,
-  attack surfaces that may or may not be properly mitigated,
-  an SLA that may or may not be sufficient

With Atlassian Cloud (YAC), you can have all the benefits of the cloud
with none of the constraints.

With YAC, you can easily deploy Atlassian applications to your AWS VPC
using cloud formation, docker and ECS (EC2 Container Service).

With YAC you get:

-  support for a scalable user base via Data Center versions of Jira,
   Confluence, and Stash
-  easy upgrades via Docker
-  an attack surface under your control
-  an SLA under your control

To use YAC, you need:

-  an AWS VPC
-  an AWS credentials file
-  an SSL cert for your app
-  a private/public key pair for your app's EC2 instances
-  an IAM role for your app's EC2 instances

To use YAC, you need to have:

-  some Cloud Formation literacy
-  some Docker/ECS literacy
-  A can-do spirit (or willingness to contact me if you get stuck)

A typical YAC stack looks like:

.. figure:: http://imgh.us/yac_vpc_3subnets.svg
   :alt: YAC Stack - 3 Subnets

   Typical Yak Stack

or

.. figure:: http://imgh.us/yac_vpc_2subnets.svg
   :alt: YAC Stack - 2 Subnets

   Typical Yak Stack

A typical YAC app looks like:

.. figure:: http://imgh.us/yac_app.svg
   :alt: YAC App

   Typical Yak App

A typical intance boot sequence is:

-  EC2 instance gets created per its auto-scaling group, then
-  ECS agent gets auto-installed, then
-  ECS agent phones-home with its cluster ID, then
-  ECS agent downloads and runs cluster-specific containers

The default versions of all YAC containers can be found in the Docker
Hub under the nordstromsets repo. Feel free to override with your
preferred containers!

Use Cases
=========

Verify your VPC
---------------

YAC uses keyword searches to find VPC ids and subnets for building its
cloud resources.

Use the following command to verify that yac can find your intended VPC
subnets.

*yac vpc -h*

Upload your Key
---------------

Your app will run under https so ...

Build your Stack
----------------

Build a stack for your Atlassian application via AWS cloud formation.
The stack includes all the AWS resources you application needs,
including ELBs, EC2 instances in an auto-scaling group, an RDS instance,
an EFS for shared home directories, and of course all the associated
security groups.

*yac stack -h*

Build your App
--------------

Each app is implemented as an ECS clusters. Each cluster includes the
containers shown in the *YAC Standard App* diagram.

*yac app -h*

After the stack and app are built, EC2 instances in your stack will
register with ECS and downlooad and run the containers in your app.
Simple!

Setup a DB
----------

Setup the DB and DB user on your RDS instance.

*yac db setup -h*

After the setup is complete, you can navigate to your Atlassian app and
execute the install wizard.

Restore Files from Backups
--------------------------

Your app includes a backups container that will backup files and
directories from your app to an S3 bucket. Files and directories can be
restored via:

*yac restore -h*

Restore a DB
------------

The DB for your app is implemented as an RDS instance. The DB will
automatically take backups of itself for a configurable number of days.
Backups can be restored via:

*yac db restore -h*

Container Dev Use Cases
-----------------------

Build Images
~~~~~~~~~~~~

Build image for a container to an EC2 instance

*yac container build -h*

Start Container
~~~~~~~~~~~~~~~

Start an individual container

*yac container start -h*

Container Log
~~~~~~~~~~~~~

View logs from a container

*yac container log -h*
