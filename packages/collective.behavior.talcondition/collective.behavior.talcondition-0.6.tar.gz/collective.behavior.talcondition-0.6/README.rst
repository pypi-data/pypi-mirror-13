.. image:: https://travis-ci.org/collective/collective.behavior.talcondition.svg?branch=master
    :target: https://travis-ci.org/collective/collective.behavior.talcondition

.. image:: https://coveralls.io/repos/collective/collective.behavior.talcondition/badge.png
  :target: https://coveralls.io/r/collective/collective.behavior.talcondition


==========================================================================
collective.behavior.talcondition
==========================================================================

This package works for dexterity (behavior) and archetypes (schema extender).

It adds two fields on a content type or class:

* tal_condition : enter a `TAL expression <http://docs.zope.org/zope2/zope2book/AppendixC.html>`_ that once evaluated will return 'True' if content should be available. By default, elements 'member', 'context' and 'portal' are available for the expression but the TAL expression context may be extended using the 'extra_expr_ctx' parameter.

* roles_bypassing_talcondition : choose the different roles for which the TAL condition will not be evaluated and always considered \'True\'

It's then possible to use the 'evaluate' method to test the TAL condition.

How to use it
=============

For AT you have to provide the ITALConditionable on your class (see testing.zcml).

For DX you just have to activate the behavior on your content type.

