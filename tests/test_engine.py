import json

import httpx
import pytest
from pydantic import ValidationError

from serp.engine import decide, live_judge, load_records, request_body, simulated_judge, write_html


def record(label='matches', confidence=0.9):
    return {'query':'read-only SQL', 'title':'SQL guide', 'snippet':'A read-only SQL tutorial with parameterized queries.', 'fixture_choice':label, 'fixture_confidence':confidence}

@pytest.mark.parametrize(('label','confidence','route'), [
    ('matches',0.9,'no_clear_intent_gap'), ('off_intent',0.9,'investigate_intent_gap'),
    ('off_intent',0.7,'human_review'), ('insufficient',0.9,'human_review')])
def test_routes(label, confidence, route):
    assert decide(simulated_judge(record(label,confidence))['answers'])['route'] == route

@pytest.mark.parametrize('bad', [float('nan'), -0.1, 1.1])
def test_invalid_confidence_rejected(bad):
    payload = simulated_judge(record())['answers']
    payload['intent']['confidence'] = bad
    with pytest.raises(ValidationError):
        decide(payload)

def test_invalid_distribution():
    payload = simulated_judge(record())['answers']
    payload['intent']['probabilities']['matches'] = 0.3
    with pytest.raises(ValidationError):
        decide(payload)

def test_official_api_contract(monkeypatch):
    monkeypatch.setenv('TYPESAFE_API_KEY','test-placeholder')
    def handler(request):
        assert str(request.url) == 'https://api.typesafe.ai/v1/systemone'
        payload = json.loads(request.content)
        assert set(payload['questions']) == {'intent','thin_evidence'}
        assert 'fixture_choice' not in payload['state']
        return httpx.Response(200,json={'model':'mock-contract-test', 'answers':simulated_judge(record())['answers'], 'usage':{'input_tokens':100}})
    result = live_judge(record(), httpx.Client(transport=httpx.MockTransport(handler)))
    assert result['model'] == 'mock-contract-test'

def test_missing_key_stops_before_network(monkeypatch):
    monkeypatch.delenv('TYPESAFE_API_KEY',raising=False)
    with pytest.raises(ValueError,match='locally'):
        live_judge(record())

def test_rate_limit_is_not_silently_simulated(monkeypatch):
    monkeypatch.setenv('TYPESAFE_API_KEY','test-placeholder')
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(429)))
    with pytest.raises(httpx.HTTPStatusError):
        live_judge(record(),client)

def test_dashboard_escapes_source_html(tmp_path):
    row = record()
    row['title'] = '<script>alert(1)</script>'
    row['decision'] = decide(simulated_judge(record())['answers'])
    target = tmp_path/'index.html'
    write_html({'mode':'fixture','disclaimer':'SIMULATED','results':[row]},target)
    text = target.read_text()
    assert '<script>' not in text and '&lt;script&gt;' in text

def test_fixture_inputs_and_payload():
    rows = load_records('data/synthetic_serp.json')
    assert len(rows) == 8
    assert request_body(rows[0], 'jev-latest')['model'] == 'jev-latest'
