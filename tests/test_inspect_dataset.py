import os
import subprocess
import tempfile
import pytest

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "inspect_dataset.py")

@pytest.fixture
def sample_csv():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("id,headline,label,image_path\n")
        f.write("1,Real news article,real,http://example.com/img1.jpg\n")
        f.write("2,Fake news article,fake,bad_path\n")
        f.write("3,Unknown article,unknown,\n")
        f.write("4,Another real,real,http://example.com/img2.png\n")
        f.write("5,Missing label,,http://example.com/img3.jpg\n")
    yield f.name
    os.remove(f.name)

@pytest.fixture
def empty_csv():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        pass
    yield f.name
    os.remove(f.name)

@pytest.fixture
def no_data_csv():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write("col1,col2\n")
    yield f.name
    os.remove(f.name)

def run_script(*args):
    cmd = ["python", SCRIPT_PATH] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True)

def test_inspect_basic_stats(sample_csv):
    res = run_script(sample_csv)
    assert res.returncode == 0
    assert "Row Count: 5" in res.stdout
    assert "id, headline, label, image_path" in res.stdout
    assert "id: int64" in res.stdout or "id: object" in res.stdout # id might be parsed as int

def test_inspect_label_stats(sample_csv):
    res = run_script(sample_csv, "--label-col", "label")
    assert res.returncode == 0
    assert "Label Statistics ('label')" in res.stdout
    assert "real: 2" in res.stdout
    assert "fake: 1" in res.stdout
    assert "unknown: 1" in res.stdout
    assert "nan: 1" in res.stdout # Missing label

def test_inspect_image_stats(sample_csv):
    res = run_script(sample_csv, "--image-col", "image_path")
    assert res.returncode == 0
    assert "Image Reference Statistics ('image_path')" in res.stdout
    assert "Missing: 1" in res.stdout
    # 'bad_path' does not have extension or http, so should be marked malformed
    assert "Malformed (basic check): 1" in res.stdout

def test_inspect_missing_file():
    res = run_script("nonexistent_file_xyz.csv")
    assert res.returncode == 1
    assert "Error: File not found" in res.stderr

def test_inspect_empty_file(empty_csv):
    res = run_script(empty_csv)
    assert res.returncode == 1
    assert "Error: File" in res.stderr
    assert "is empty" in res.stderr

def test_inspect_no_data_csv(no_data_csv):
    # Depending on pandas, reading just header might work but len(df)==0
    res = run_script(no_data_csv)
    assert res.returncode == 0
    assert "Row Count: 0" in res.stdout
    assert "No data to preview." in res.stdout

def test_inspect_with_registry(sample_csv):
    # We will invoke the script with --dataset-id "example_fake_news_dataset"
    # But since it points to a mock path by default, we'll patch the env var
    # to point to the directory of sample_csv, and dynamically register a new dataset config
    # to match sample_csv name, or we can just mock it if we can.
    # Because we run the script in a subprocess, we need the script to see a valid registry.
    # The script loads `registry` which loads `example_config`.
    # Let's create a temporary registry script or just mock the environment variable
    # and use the default example if we can, but we can't easily modify the global registry of the subprocess.
    # Instead, we will write a temporary python script that registers a custom dataset and calls inspect_dataset.

    test_runner_script = """
import sys
import os
sys.path.insert(0, {repo_root_repr})
from src.dataset_registry import registry, DatasetConfig

config = DatasetConfig(
    identifier="test_mock_dataset",
    display_name="Mock Dataset",
    local_file_path="{file_name}",
    expected_format="csv",
    label_mapping={{"real": "real", "fake": "fake"}},
    text_field_mapping={{"headline": "headline"}},
    image_reference_field="image_path"
)
registry.register(config)

from scripts.inspect_dataset import parse_args, inspect_dataset
sys.argv = ['inspect_dataset.py', '--dataset-id', 'test_mock_dataset', '--label-col', 'label']
args = parse_args()
inspect_dataset(args)
"""

    script_dir = os.path.dirname(sample_csv)
    file_name = os.path.basename(sample_csv)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write(test_runner_script.format(file_name=file_name, repo_root_repr=repr(repo_root)))
        test_script_path = f.name

    env = os.environ.copy()
    env["PROJECT_DATA_DIR"] = script_dir

    res = subprocess.run(["python", test_script_path], capture_output=True, text=True, env=env)

    os.remove(test_script_path)

    assert res.returncode == 0
    assert "File Path:" in res.stdout
    assert file_name in res.stdout
    assert "Row Count: 5" in res.stdout
    assert "Image Reference Statistics ('image_path')" in res.stdout
