from dataclasses import dataclass
from enum import Enum
from typing import Any


class Operator(Enum):
    MATCH = 'match'
    TERM = 'term'
    RANGE = 'range'


class Field(Enum):
    DATA_CENTER = 'th_odatis_centre_donnees.default'
    PLATFORMS = 'platforms'
    ID = '_id'
    TITLE = 'title'
    ABSTRACT = 'abstract'
    KEYWORDS = 'keywords'
    DATE = 'date'


class ClauseType(Enum):
    MUST = 'must'
    MUST_NOT = 'must_not'
    SHOULD = 'should'
    FILTER = 'filter'


@dataclass
class Clause:
    clause_type: ClauseType
    operator: Operator
    field: Field
    value: Any


class GeoNetworkQueryBuilder:
    """Geonetwork query builder.

    Supports: must, must_not, should, filter.
    """

    def __init__(self):
        self._from = 0
        self._size = 20
        self.clauses: dict[ClauseType, list[dict[str, Any]]] = {
            ct: []
            for ct in ClauseType
        }

    def _add_clause(self, clause_type: ClauseType, operator: Operator,
                    field: Field, value: Any):
        self.clauses[clause_type].append(
            {operator.value: {
                field.value: value
            }})
        return self

    def must_match(self, field: Field, value: Any):
        return self._add_clause(ClauseType.MUST, Operator.MATCH, field, value)

    def must_term(self, field: Field, value: Any):
        return self._add_clause(ClauseType.MUST, Operator.TERM, field, value)

    def must_not_match(self, field: Field, value: Any):
        return self._add_clause(ClauseType.MUST_NOT, Operator.MATCH, field,
                                value)

    def must_not_term(self, field: Field, value: Any):
        return self._add_clause(ClauseType.MUST_NOT, Operator.TERM, field,
                                value)

    def should_match(self, field: Field, value: Any):
        return self._add_clause(ClauseType.SHOULD, Operator.MATCH, field,
                                value)

    def should_term(self, field: Field, value: Any):
        return self._add_clause(ClauseType.SHOULD, Operator.TERM, field, value)

    def filter_term(self, field: Field, value: Any):
        return self._add_clause(ClauseType.FILTER, Operator.TERM, field, value)

    def filter_range(self, field: Field, range_query: dict[str, Any]):
        return self._add_clause(ClauseType.FILTER, Operator.RANGE, field,
                                range_query)

    def build(self) -> dict[str, Any]:
        bool_query = {
            clause_type.value: clauses
            for clause_type, clauses in self.clauses.items() if clauses
        }

        return {
            'from': self._from,
            'size': self._size,
            'query': {
                'bool': bool_query
            }
        }
