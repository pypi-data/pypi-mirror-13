.. :changelog:

History
=======

Pending
-------

* Next version release notes here

1.4.0 (2016-01-07)
------------------

* ``ec2-ssh`` rewritten in Python. As part of this, the automatic 'pretty
  prompt' has been removed.

1.3.0 (2016-01-06)
------------------

* Forked by YPlan
* Output from ec2-host is now in random order, allowing ec2-ssh to spread
  logins between similar instances
* Python 3 compatibility

1.2.1 (2011-11-27)
------------------
* Fix issue when ec2-host finds one offline instance with same name as an online instance

1.2 (2011-11-27)
----------------

* Merged pull requests to add region and tag support

1.1.1 (2011-11-17)
------------------

* Add line echoing host before establishing SSH connection

1.1 (2011-11-15)
----------------

* override prompt (PS1) to show tag name

1.0 (2011-09-05)
----------------

* initial release
