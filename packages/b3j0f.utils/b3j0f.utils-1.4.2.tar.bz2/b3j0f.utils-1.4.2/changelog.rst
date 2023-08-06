ChangeLog
=========

1.4.2 (2015/02/22)
------------------

- add requirements.txt and changelog.rst in building packages.

1.4.1 (2015/02/21)
------------------

- add the function iterable.hashiter in order to hash not hashable iterables.
- add runtime.getcodeobj function in order to produce a code object from old code object.

1.4.0 (2015/12/22)
------------------

- add the parameter `scope` in the function `path.lookup`.
- add safe parameter in the function `path.lookup`.
- use static safe scope in the module `runtime`.

1.3.0 (2015/11/18)
------------------

- add the decorator b3j0f.path.alias function for quick registering python objects.
- change contact address.

1.2.0 (2015/11/8)
-----------------

- add dependency to the modules six and future and remove version functions.
- use relative imports in UTs.

1.1.0 (2015/11/8)
-----------------

- add functions last, itemat and slice in the iterable module.

1.0.1 (2015/10/29)
------------------

- add in the module runtime:
   - the function _safe_builtins
   - the variable SAFE_BUILTINS
   - the functions safe_eval and safe_exec used to eval/exec python code without IO functions.
- add the builtins module in the module version.
- add description of tu, version and runtime in the readme.

1.0.0 (2015/10/20)
------------------

- set stable version.

0.10.4 (2015/10/02)
-------------------

- update the module version with python3 and python2 common modules with different names.
- add support of pyhton3.5.

0.10.3 (15/09/28)
-----------------

- add range and raw_input definition in the module version in order to use xrange whatever python2/3 execution environment, and raw_input in python3.

0.10.2 (15/09/28)
-----------------

- auto generate documentation in the addproperties decorator.

0.10.1 (15/09/28)
-----------------

- improve addproperties execution time and unittests.

0.10.0 (15/09/28)
-----------------

- add addproperties decorator in the module property.

0.9.5 (15/07/14)
----------------

- add __version_info__ in the base package.
- fix method proxy generation in the function b3j0f.utils.proxy.proxify_elt.
- add public parameter in b3j0f.utils.proxy.proxify_elt.

0.9.4 (15/06/27)
----------------

- add __getproxy__ instance method name in order to specialize the generation of a proxy from the elt to proxify.

0.9.3 (15/06/14)
----------------

- add docs directory in order to be hosted by readthedocs.

0.9.2 (15/06/13)
----------------

- add dependency to ordereddict.

0.9.1 (15/06/13)
----------------

- add shields.io badges.

0.9.0 (15/05/20)
--------------

- add wheel distribution package.

0.8.7 (15/05/20)
----------------

- Fix UTs.

0.8.6 (20/05/15)
----------------

- Add definition of getcallargs and OrderedDict in b3j0f.utils.version module.
- Move changelog from README to a separate documentation page.

0.8.5 (16/02/15)
----------------

- Add proxy module.
