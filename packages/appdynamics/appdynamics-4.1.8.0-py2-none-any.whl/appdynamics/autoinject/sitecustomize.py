# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Trick Python into loading the agent.

"""

import logging
import os
import sys

try:
    sys.path.remove(os.path.dirname(__file__))
except ValueError:
    pass

try:
    import appdynamics.agent
    appdynamics.agent.configure()
    appdynamics.agent.bootstrap()
except:
    logger = logging.getLogger('appdynamics.agent')
    logger.exception('Exception in agent startup.')
finally:
    try:
        appdynamics.agent.remove_autoinject()
    except:
        pass
