import pytest
from .extract import load_row_from_csv
import os


@pytest.fixture
def sample_csv_file(tmpdir):
    sample_filename = os.path.join(tmpdir, "sample_data.csv")
    with open(sample_filename, mode="w") as f:
        f.write("Header1,Header2,Header3\n")
        f.write("A,B,C\n")
        f.write("D,E,F\n")
        f.write("G,H,I\n")
    return sample_filename


def test_load_row_from_csv(sample_csv_file):
    # Call the function to load the first column
    result = load_row_from_csv(sample_csv_file, row_index=0, has_header=True)

    expected_result = ["A", "B", "C"]
    assert result == expected_result

    result = load_row_from_csv(sample_csv_file, row_index=1, has_header=True)

    expected_result = ["D", "E", "F"]
    assert result == expected_result
