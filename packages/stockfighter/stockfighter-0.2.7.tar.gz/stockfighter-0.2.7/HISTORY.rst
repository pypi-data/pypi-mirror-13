=======
History
=======

0.2.7 (2015-12-21)
------------------

* Fix status_for_all_orders_in_a_stock URL
* Fix GM restart/resume/etc failing due to broken format strings

0.2.6 (2015-12-14)
------------------

* Fix place_new_order to actually pass price. Novel!

0.2.5 (2015-12-14)
------------------

* Python3 re-compatibility 
* Fix status_for_all_orders endpoint

0.2.4 (2015-12-12)
------------------

* Fix some outlying GM implementation bugs
* Add test for basic GM client object instantiation

0.2.3 (2015-12-12)
------------------

* Tests now also assert the API is responding w/ good "ok" values, not just HTTP 200s.
* Py 3.5 testing included

0.2.2 (2015-12-12)
------------------

* Fix testing and implementation for place_order

0.2.2 (2015-12-11)
------------------

* Make py2 and py3 compatibility a thing, guaranteed by Tox and Travis.

0.2.1 (2015-12-11)
------------------

* Working README and quick install

0.2.0 (2015-12-11)
------------------

* All API functions implemented and tested

0.1.0 (2015-12-11)
------------------

* First release on PyPI.
