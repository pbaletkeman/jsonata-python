# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long

"""
JFunctionSignatureValidation module for Jsonata Python implementation.
Defines the JFunctionSignatureValidation interface for validating function signatures in JSONata.
"""


from typing import Any, Optional


class JFunctionSignatureValidation:
    """
    Interface for validating function signatures in JSONata.
    """

    def validate(self, args: Optional[Any], context: Optional[Any]) -> Optional[Any]:
        """
        Validate the arguments against the function signature.
        Args:
            args: Arguments to validate.
            context: Context for validation.
        Returns:
            Validated arguments or original args if no signature.
        """
        # Should be implemented by subclasses.
        raise NotImplementedError("Subclasses must implement validate method.")
