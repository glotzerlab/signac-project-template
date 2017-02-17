import warnings
from distutils.version import StrictVersion

import signac
import flow

from .project import get_project

SIGNAC_MIN_VERSION = '0.2.8'
FLOW_MIN_VERSION = '0.1.9'

if StrictVersion(signac.__version__) < StrictVersion(SIGNAC_MIN_VERSION):
    warnings.warn(
        "The signac project template is tested for signac "
        "version {}, your version: {}.".format(
            SIGNAC_MIN_VERSION, signac.__version__))

if StrictVersion(flow.__version__) < StrictVersion(FLOW_MIN_VERSION):
    warnings.warn(
        "The signac project template is tested for signac-flow "
        "version {}, your version: {}.".format(
            FLOW_MIN_VERSION, flow.__version__))

__all__ = ['get_project']
