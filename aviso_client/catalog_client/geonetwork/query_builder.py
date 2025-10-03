
from typing import Any

class InvalidFieldError(Exception):
    pass


class GeoNetworkQueryBuilder:
    """
    Geonetwork query builder.
    Support of must, must_not, should, filter.
    """
    ALLOWED_OPERATORS = {"match", "term", "range"}
    VALID_FIELDS = {
        "th_odatis_centre_donnees.default",
        "platforms",
        "_id",
        "title",
        "abstract",
        "keywords",
        "date",
    }

    def __init__(self):
        self._from = 0
        self._size = 20
        self.clauses = {
            "must": [],
            "must_not": [],
            "should": [],
            "filter": []
        }

    def _validate_field(self, field: str):
        if field not in self.VALID_FIELDS:
            raise InvalidFieldError(f"Invalid field: '{field}'")

    def _add_clause(self, clause_type: str, operator: str, field: str, value: Any):
        if clause_type not in self.clauses:
            raise ValueError(f"Invalid clause: {clause_type}")
        if operator not in self.ALLOWED_OPERATORS:
            raise ValueError(f"Invalid operator: {operator}")
        self._validate_field(field)

        self.clauses[clause_type].append({operator: {field: value}})
        return self

    def must_match(self, field: str, value: Any):
        return self._add_clause("must", "match", field, value)

    def must_term(self, field: str, value: Any):
        return self._add_clause("must", "term", field, value)

    def must_not_match(self, field: str, value: Any):
        return self._add_clause("must_not", "match", field, value)

    def must_not_term(self, field: str, value: Any):
        return self._add_clause("must_not", "term", field, value)

    def should_match(self, field: str, value: Any):
        return self._add_clause("should", "match", field, value)

    def should_term(self, field: str, value: Any):
        return self._add_clause("should", "term", field, value)

    def filter_term(self, field: str, value: Any):
        return self._add_clause("filter", "term", field, value)

    def filter_range(self, field: str, range_query: dict[str, Any]):
        return self._add_clause("filter", "range", field, range_query)

    def from_offset(self, offset: int):
        self._from = offset
        return self

    def size(self, size: int):
        self._size = size
        return self

    def build(self) -> dict[str, Any]:
        bool_query = {
            k: v for k, v in self.clauses.items() if v
        }

        payload = {
            "from": self._from,
            "size": self._size,
            "query": {
                "bool": bool_query
            }
        }

        return payload