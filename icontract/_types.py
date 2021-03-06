"""Define data structures shared among the modules."""
import inspect
import reprlib
from typing import Callable, Optional, Union, Set, List, Any  # pylint: disable=unused-import

import icontract._globals

# pylint: disable=protected-access


class Contract:
    """Represent a contract to be enforced as a precondition, postcondition or as an invariant."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self,
                 condition: Callable[..., bool],
                 description: Optional[str] = None,
                 a_repr: reprlib.Repr = icontract._globals.aRepr,
                 error: Optional[Union[Callable[..., Exception], type]] = None,
                 location: Optional[str] = None) -> None:
        """
        Initialize.

        :param condition: condition predicate
        :param description: textual description of the contract
        :param a_repr: representation instance that defines how the values are represented
        :param error:
            if given as a callable, ``error`` is expected to accept a subset of function arguments
            (*e.g.*, also including ``result`` for perconditions, only ``self`` for invariants *etc.*) and return
            an exception. The ``error`` is called on contract violation and the resulting exception is raised.

            Otherwise, it is expected to denote an Exception class which is instantiated with the violation message
            and raised on contract violation.
        :param location: indicate where the contract was defined (*e.g.*, path and line number)
        """
        # pylint: disable=too-many-arguments
        self.condition = condition

        self.condition_args = list(inspect.signature(condition).parameters.keys())  # type: List[str]
        self.condition_arg_set = set(self.condition_args)  # type: Set[str]

        self.description = description
        self._a_repr = a_repr

        self.error = error
        self.error_args = None  # type: Optional[List[str]]
        self.error_arg_set = None  # type: Optional[Set[str]]
        if error is not None and (inspect.isfunction(error) or inspect.ismethod(error)):
            self.error_args = list(inspect.signature(error).parameters.keys())
            self.error_arg_set = set(self.error_args)

        self.location = location


class Snapshot:
    """Define a snapshot of an argument *prior* to the function invocation that is later supplied to a postcondition."""

    def __init__(self, capture: Callable[..., Any], name: Optional[str] = None) -> None:
        """
        Initialize.

        :param capture:
            function to capture the snapshot accepting a single argument (from a set of arguments
            of the original function)

        :param name: name of the captured variable in OLD that is passed to postconditions

        """
        self.capture = capture

        args = list(inspect.signature(capture).parameters.keys())  # type: List[str]

        if len(args) > 1:
            raise TypeError("The capture function of a snapshot expects only a single argument.")

        if len(args) == 0 and name is None:
            raise ValueError("You must name a snapshot if no argument was given in the capture function.")

        if name is None:
            name = args[0]

        assert name is not None, "Expected ``name`` to be set in the preceding execution paths."
        self.name = name

        self.arg = None  # type: Optional[str]
        if len(args) == 1:
            self.arg = args[0]
        else:
            assert len(args) == 0, "There can be at most one argument to a snapshot capture, but got: {}".format(args)
