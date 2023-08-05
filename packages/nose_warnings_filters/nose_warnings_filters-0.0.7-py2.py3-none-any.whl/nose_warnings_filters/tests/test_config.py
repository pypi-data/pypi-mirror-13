import nose_warnings_filters as nwf
import warnings

import nose.tools as nt


import nose_warnings_filters.tests.utils as utils

def test():
    nwf.WarningFilter()
    
def test_ignore():
    with warnings.catch_warnings(record=True) as w:
        warnings.warn('This should be ignored', utils.MyWarningIgnore)
        nt.assert_equals(w, [])

def test_error():
    with nt.assert_raises(utils.MyWarningError):
        warnings.warn('This should error', utils.MyWarningError)
