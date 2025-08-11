from typing import Optional, List

from ..models.config import CheckContext
from ..field_types import FieldType
from .base import BaseField
from .text import TextField
from .number import NumberField
from .boolean import BooleanField
from .datetime import DateTimeField
from .lookup import LookupField


class FieldFactory:
    @staticmethod
    def create(
        field_type: FieldType,
        code: str,
        title: Optional[str],
        readonly: Optional[bool],
        strict_title: bool,
        context: CheckContext,
        lookup_values: Optional[List[str]] = None,
    ) -> BaseField:
        if field_type == FieldType.TEXT:
            return TextField(code, title, readonly, strict_title, context)
        if field_type == FieldType.NUMBER:
            return NumberField(code, title, readonly, strict_title, context)
        if field_type == FieldType.BOOLEAN:
            return BooleanField(code, title, readonly, strict_title, context)
        if field_type == FieldType.DATETIME:
            return DateTimeField(code, title, readonly, strict_title, context)
        if field_type == FieldType.LOOKUP:
            return LookupField(code, title, readonly, strict_title, context, expected_options=lookup_values or [])
        return TextField(code, title, readonly, strict_title, context)
