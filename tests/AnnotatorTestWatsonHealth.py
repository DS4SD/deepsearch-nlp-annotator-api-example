import pytest
from nlp_annotator_api.annotators.WatsonHealthAnnotator import WatsonHealthAnnotator

object_type = "text"


@pytest.fixture
def annotator():
    return WatsonHealthAnnotator()


def test_empty_returns_empty(annotator):
    texts = []

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == 0


def test_annotates_one(annotator):
    texts = ['Hello']

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)


def test_annotates_many_texts(annotator):
    texts = ['Hello', 'world']

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)


def test_handles_one_empty_input(annotator):
    texts = ['']

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)


def test_handles_many_empty_inputs(annotator):
    texts = ['', '']

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)


def test_handles_mixed_empty_and_non_empty_inputs(annotator):
    texts = ['', 'Hello']

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)


def test_skips_very_large_input(annotator):
    with open('./tests/large_text.txt', 'r') as text_reader:
        texts = [text_reader.read()]

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)


def test_skips_very_large_inputs_but_keeps_small_ones_after(annotator):
    with open('./tests/large_text.txt', 'r') as text_reader:
        texts = [text_reader.read(), 'Hello again']

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)


def test_skips_very_large_inputs_but_keeps_small_ones_before(annotator):
    with open('./tests/large_text.txt', 'r') as text_reader:
        texts = ['Hello again', text_reader.read()]

    entities = annotator.annotate_batched_entities(object_type, texts, annotator.get_entity_names())

    assert len(entities) == len(texts)
