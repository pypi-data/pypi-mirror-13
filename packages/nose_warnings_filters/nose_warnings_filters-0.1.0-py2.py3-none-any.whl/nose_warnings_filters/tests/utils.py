"""
Utils for testing

Mainly need dummy warnigns that cannot be defined in the same module as
the one where the tests are defined.
"""

class MyWarningError(Warning):pass
class MyWarningIgnore(Warning):pass
