.. :changelog:

History
=======

0.4.6 (2015/10/12)
------------------

- Added rate limiting to the client

0.4.5 (2015/10/01)
------------------

- Added container magic methods to Resource class

0.4.4 (2015/09/30)
----------------

- Merged some changes from a fork, updated tests to match
- Refactored the api clients, restructured the resources to include all API endpoints
- Added Search resources
- Resources now work by passing an API_KEY through to them or settings the environment variable DUEDIL_API_KEY
- Resources need filling out and fixing together with related resources
- Skeletons of the International API is there & the lite API


0.3 (2015/02/27)
----------------

- Company and Directors searches are returning a result set instead of a list
- Change in ordering of search results


0.2 (2014/12/10)
----------------

- add v3 lite api

0.1 (2014/12/09)
----------------

- Initial version on PyPI - only v3pro api partially implemented
