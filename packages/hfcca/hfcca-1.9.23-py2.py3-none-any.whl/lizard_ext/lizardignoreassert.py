'''
This is an extension of lizard, that ignores the CCN within
the assertion.
'''
from lizard import CodeStateMachine


class LizardExtension(CodeStateMachine):  # pylint: disable=R0903

    def _state_global(self, token):
        if token in ("assert", "static_assert"):
            self._state = self.in_assertion

    @CodeStateMachine.read_inside_brackets_then("()", "_state_global")
    def in_assertion(self, token):
        if token in ("&&", "||", "?"):
            self.context.add_condition(-1)
