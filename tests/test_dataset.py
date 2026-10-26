from src.data.dataset import load_dataset
import tempfile
import os

def test_load_dataset_jsonl():
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_path = os.path.join(tmpdir, "dataset.jsonl")
        with open(dataset_path, "w") as f:
            f.write('{"article_id": "1", "headline": "True news", "label": "real"}\n')
            f.write('{"article_id": "2", "headline": "Fake news", "label": "fake"}\n')

        records = load_dataset(dataset_path)
        assert len(records) == 2
        assert records[0]["article_id"] == "1"
        assert records[1]["label"] == "fake"

def test_load_dataset_json_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_path = os.path.join(tmpdir, "dataset.json")
        with open(dataset_path, "w") as f:
            f.write('[{"article_id": "1", "headline": "True news", "label": "real"}]')

        records = load_dataset(dataset_path)
        assert len(records) == 1
        assert records[0]["article_id"] == "1"
