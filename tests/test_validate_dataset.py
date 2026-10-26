import json
import os
import subprocess
import tempfile

def test_validate_dataset_good_data():
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_path = os.path.join(tmpdir, "dataset.jsonl")
        with open(dataset_path, "w") as f:
            f.write('{"article_id": "1", "headline": "True news", "label": "real"}\n')
            f.write('{"article_id": "2", "headline": "Fake news", "label": "fake"}\n')

        output_dir = os.path.join(tmpdir, "output")
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "validate_dataset.py")

        result = subprocess.run(
            [script_path, dataset_path, "--output-dir", output_dir, "--fail-on-critical"],
            capture_output=True, text=True
        )

        assert result.returncode == 0

        with open(os.path.join(output_dir, "report.json")) as f:
            report = json.load(f)

        assert report["total_records"] == 2
        assert report["missing_required"] == 0
        assert report["duplicate_ids"] == 0
        assert not report["critical_failures"]

def test_validate_dataset_critical_failure():
    with tempfile.TemporaryDirectory() as tmpdir:
        dataset_path = os.path.join(tmpdir, "dataset.jsonl")
        with open(dataset_path, "w") as f:
            f.write('{"headline": "Missing id", "label": "real"}\n')

        output_dir = os.path.join(tmpdir, "output")
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "validate_dataset.py")

        result = subprocess.run(
            [script_path, dataset_path, "--output-dir", output_dir, "--fail-on-critical"],
            capture_output=True, text=True
        )

        assert result.returncode == 1

        with open(os.path.join(output_dir, "report.json")) as f:
            report = json.load(f)

        assert report["total_records"] == 1
        assert report["missing_required"] == 1
        assert report["critical_failures"]

def test_validate_dataset_cross_split_duplicates():
    with tempfile.TemporaryDirectory() as tmpdir:
        split1_path = os.path.join(tmpdir, "split1.jsonl")
        with open(split1_path, "w") as f:
            f.write('{"article_id": "1", "headline": "True news", "label": "real"}\n')

        split2_path = os.path.join(tmpdir, "split2.jsonl")
        with open(split2_path, "w") as f:
            f.write('{"article_id": "1", "headline": "Same id across splits", "label": "fake"}\n')

        output_dir = os.path.join(tmpdir, "output")
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", "validate_dataset.py")

        result = subprocess.run(
            [script_path, split1_path, split2_path, "--output-dir", output_dir, "--fail-on-critical"],
            capture_output=True, text=True
        )

        assert result.returncode == 1

        with open(os.path.join(output_dir, "report.json")) as f:
            report = json.load(f)

        assert report["cross_split_duplicate_ids"] == 1
        assert report["critical_failures"]
