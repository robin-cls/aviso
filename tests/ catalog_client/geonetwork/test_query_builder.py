import pytest

from aviso_client.catalog_client.geonetwork.query_builder import (
    GeoNetworkQueryBuilder,
    InvalidFieldError,
)

VALID_FIELD = 'platforms'
INVALID_FIELD = 'invalid_field'


def test_must_match_clause():
    builder = GeoNetworkQueryBuilder()
    payload = builder.must_match('platforms', 'SWOT').build()

    assert 'must' in payload['query']['bool']
    assert payload['query']['bool']['must'][0] == {
        'match': {
            'platforms': 'SWOT'
        }
    }


def test_must_not_term_clause():
    builder = GeoNetworkQueryBuilder()
    payload = builder.must_not_term('_id', 'some-id').build()

    assert 'must_not' in payload['query']['bool']
    assert payload['query']['bool']['must_not'][0] == {
        'term': {
            '_id': 'some-id'
        }
    }


def test_should_match_clause():
    builder = GeoNetworkQueryBuilder()
    payload = builder.should_match('platforms', 'Sentinel-3').build()

    assert 'should' in payload['query']['bool']
    assert payload['query']['bool']['should'][0] == {
        'match': {
            'platforms': 'Sentinel-3'
        }
    }


def test_filter_range_clause():
    builder = GeoNetworkQueryBuilder()
    payload = builder.filter_range('date', {
        'gte': '2020-01-01',
        'lte': '2022-01-01'
    }).build()

    assert 'filter' in payload['query']['bool']
    assert payload['query']['bool']['filter'][0] == {
        'range': {
            'date': {
                'gte': '2020-01-01',
                'lte': '2022-01-01'
            }
        }
    }


def test_combined_clauses():
    builder = GeoNetworkQueryBuilder()
    payload = (builder.must_match('platforms', 'SWOT').must_not_term(
        '_id', '123').should_term('platforms', 'Sentinel-3').filter_term(
            'th_odatis_centre_donnees.default', 'CDS-AVISO').build())

    bool_query = payload['query']['bool']
    assert 'must' in bool_query
    assert 'must_not' in bool_query
    assert 'should' in bool_query
    assert 'filter' in bool_query

    assert bool_query['must'][0]['match']['platforms'] == 'SWOT'
    assert bool_query['must_not'][0]['term']['_id'] == '123'


def test_offset_and_size():
    builder = GeoNetworkQueryBuilder()
    payload = builder.from_offset(10).size(50).build()

    assert payload['from'] == 10
    assert payload['size'] == 50


def test_invalid_field_raises_error():
    builder = GeoNetworkQueryBuilder()
    with pytest.raises(InvalidFieldError):
        builder.must_match('invalid_field', 'test')


def test_invalid_operator_raises_error():
    builder = GeoNetworkQueryBuilder()
    with pytest.raises(ValueError):
        builder._add_clause('must', 'unsupported_operator', 'platforms',
                            'test')


def test_invalid_clause_type_raises_error():
    builder = GeoNetworkQueryBuilder()
    with pytest.raises(ValueError):
        builder._add_clause('invalid_clause', 'match', 'platforms', 'test')
