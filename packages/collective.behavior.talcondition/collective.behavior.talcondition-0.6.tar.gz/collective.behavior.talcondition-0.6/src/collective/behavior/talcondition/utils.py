# -*- coding: utf-8 -*-
import logging
from Products.CMFCore.Expression import Expression, createExprContext
from plone import api

logger = logging.getLogger('collective.behavior.talcondition')
WRONG_TAL_CONDITION = "The TAL expression '%s' for element at '%s' is wrong.  Original exception : %s"


def evaluateExpressionFor(obj, extra_expr_ctx={}):
    """Evaluate the expression stored in 'tal_condition' of given p_obj.
    """
    # get tal_condition
    tal_condition = obj.tal_condition and obj.tal_condition.strip() or ''

    roles_bypassing_talcondition = obj.roles_bypassing_talcondition

    if hasattr(obj, 'context'):
        obj = obj.context
    return _evaluateExpression(obj,
                               expression=tal_condition,
                               roles_bypassing_expression=roles_bypassing_talcondition,
                               extra_expr_ctx=extra_expr_ctx)


def _evaluateExpression(obj,
                        expression,
                        roles_bypassing_expression=[],
                        extra_expr_ctx={},
                        empty_expr_is_true=True):
    """Evaluate given p_expression extending expression context with p_extra_expr_ctx."""
    if not expression.strip():
        return empty_expr_is_true

    res = True
    member = api.user.get_current()
    for role in roles_bypassing_expression:
        if member.has_role(str(role), obj):
            return res
    portal = api.portal.get()
    ctx = createExprContext(obj.aq_inner.aq_parent,
                            portal,
                            obj)
    ctx.setGlobal('member', member)
    ctx.setGlobal('context', obj)
    ctx.setGlobal('portal', portal)
    for extra_key, extra_value in extra_expr_ctx.items():
        ctx.setGlobal(extra_key, extra_value)
    try:
        res = Expression(expression)(ctx)
    except Exception, e:
        logger.warn(WRONG_TAL_CONDITION % (expression,
                                           obj.absolute_url(),
                                           str(e)))
        res = False
    return res


def applyExtender(portal, meta_types):
    """
      We add some fields using archetypes.schemaextender to every given p_meta_types.
    """
    logger.info("Adding talcondition fields : updating the schema for meta_types %s" % ','.join(meta_types))
    at_tool = api.portal.get_tool('archetype_tool')
    catalog = api.portal.get_tool('portal_catalog')
    catalog.ZopeFindAndApply(portal,
                             obj_metatypes=meta_types,
                             search_sub=True,
                             apply_func=at_tool._updateObject)
    logger.info("Done!")
