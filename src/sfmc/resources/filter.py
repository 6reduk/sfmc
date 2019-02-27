"""Search filter logic"""

from datetime import date, datetime


class SimpleOperator:
    EQUALS = 'equals'
    NOT_EQUALS = 'notEquals'
    IS_NULL = 'isNull'
    IS_NOT_NULL = 'isNotNull'
    GREATER_THAN = 'greaterThan'
    GREATER_THAN_OR_EQUAL = 'greaterThanOrEqual'
    LESS_THAN = 'lessThan'
    LESS_THAN_OR_EQUAL = 'lessThanOrEqual'
    BETWEEN = 'between'
    LIKE = 'like'
    IN = 'IN'


class LogicalOperator:
    AND = 'AND'
    OR = 'OR'


class SearchFilter:

    def __init__(self, property_name=None, simple_operator=None, value=None, value_type=None, logical_operator=None,
                 left_operand=None, right_operand=None):
        self.property_name = property_name
        self.simple_operator = simple_operator
        self.value_type = value_type
        self.value = value
        self.logical_operator = logical_operator
        self.left_operand = left_operand
        self.right_operand = right_operand

    def payload(self):
        data = None
        if self.logical_operator is not None:
            data = {
                'LeftOperand': self.left_operand.payload(),
                'LogicalOperator': self.logical_operator,
                'RightOperand': self.right_operand.payload()
            }
        else:
            data = {
                'Property': self.property_name,
                'SimpleOperator': self.simple_operator,
            }

            if self.value is not None:  # check is_null and is_not null operation
                data[self.value_type] = self.value

        return data

    @classmethod
    def __complex_filter(cls, operator, left, right):
        if not isinstance(left, cls) or not isinstance(right, cls):
            raise TypeError('All operands must be instance of {} class'.format(cls.__class__.__name__))

        return cls(logical_operator=operator, left_operand=left, right_operand=right)

    @classmethod
    def both(cls, left, right):
        return cls.__complex_filter(LogicalOperator.AND, left, right)

    @classmethod
    def one_from(cls, left, right):
        return cls.__complex_filter(LogicalOperator.OR, left, right)

    @classmethod
    def __simple_filter(cls, operator, property_name, value=None):
        value_type = 'Value'
        if isinstance(value, date) or isinstance(value, datetime):
            value_type = 'DateValue'

        f = None

        if value is None:
            f = cls(property_name=property_name, simple_operator=operator, value_type=value_type)
        else:
            f = cls(property_name=property_name, simple_operator=operator, value_type=value_type, value=value)

        return f

    @classmethod
    def equals(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.EQUALS, property_name, value)

    @classmethod
    def not_equals(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.NOT_EQUALS, property_name, value)

    @classmethod
    def is_null(cls, property_name):
        return cls.__simple_filter(SimpleOperator.NOT_EQUALS, property_name)

    @classmethod
    def is_not_null(cls, property_name):
        return cls.__simple_filter(SimpleOperator.NOT_EQUALS, property_name)

    @classmethod
    def greater_than(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.GREATER_THAN, property_name, value)

    @classmethod
    def greater_than_or_equal(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.GREATER_THAN_OR_EQUAL, property_name, value)

    @classmethod
    def less_than(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.LESS_THAN, property_name, value)

    @classmethod
    def less_than_or_equal(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.LESS_THAN_OR_EQUAL, property_name, value)

    @classmethod
    def between(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.BETWEEN, property_name, value)

    @classmethod
    def like(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.LIKE, property_name, value)

    @classmethod
    def in_array(cls, property_name, value):
        return cls.__simple_filter(SimpleOperator.IN, property_name, value)
