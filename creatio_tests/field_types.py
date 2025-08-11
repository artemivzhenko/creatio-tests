from enum import Enum


class FieldType(Enum):
    TEXT = "text"
    BOOLEAN = "boolean"
    LOOKUP = "lookup"
    NUMBER = "number"
    DATETIME = "datetime"
