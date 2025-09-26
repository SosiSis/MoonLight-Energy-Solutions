import pytest
import pandas as pd
import tempfile
import os
from scripts.data_load import load_csv, load_country_files, EXPECTED_COLUMNS


class TestDataLoad:
    """Test suite for data loading functions"""

    @pytest.fixture
    def sample_csv_data(self):
        """Create sample CSV data for testing"""
        return """Timestamp,GHI,DNI,DHI,ModA,ModB,Tamb,RH,WS,WSgust,WSstdev,WD,WDstdev,BP,Cleaning,Precipitation,TModA,TModB,Comments
2023-01-01 06:00,0,0,0,0.0,0.0,25.5,60.0,2.1,3.2,0.5,180.0,15.0,1013.0,0,0.0,25.0,25.1,
2023-01-01 07:00,150,120,30,145.0,148.0,26.0,58.0,2.5,3.8,0.3,175.0,12.0,1013.2,0,0.0,26.5,26.8,
2023-01-01 08:00,350,280,70,340.0,345.0,27.5,55.0,3.1,4.5,0.4,170.0,10.0,1013.5,0,0.0,28.0,28.2,
2023-01-01 09:00,550,450,100,535.0,540.0,29.0,52.0,3.8,5.2,0.5,165.0,8.0,1013.8,0,0.0,30.5,30.8,
"""

    @pytest.fixture
    def temp_csv_file(self, sample_csv_data):
        """Create a temporary CSV file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(sample_csv_data)
            temp_path = f.name
        yield temp_path
        # Cleanup
        os.unlink(temp_path)

    def test_load_csv_basic(self, temp_csv_file):
        """Test basic CSV loading functionality"""
        df = load_csv(temp_csv_file)

        # Check that dataframe is loaded
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4

        # Check expected columns are present
        for col in EXPECTED_COLUMNS:
            if col != 'Comments':  # Comments column is empty in sample
                assert col in df.columns

    def test_load_csv_timestamp_parsing(self, temp_csv_file):
        """Test that timestamps are parsed correctly"""
        df = load_csv(temp_csv_file)

        # Check timestamp column type
        assert pd.api.types.is_datetime64_any_dtype(df['Timestamp'])

        # Check timestamps are sorted
        assert df['Timestamp'].is_monotonic_increasing

        # Check specific timestamp values
        expected_timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 09:00', freq='H')
        pd.testing.assert_series_equal(df['Timestamp'].reset_index(drop=True), 
                                      pd.Series(expected_timestamps, name='Timestamp'))

    def test_load_csv_no_parse_dates(self, temp_csv_file):
        """Test loading CSV without date parsing"""
        df = load_csv(temp_csv_file, parse_dates=False)

        # Timestamp should remain as string
        assert df['Timestamp'].dtype == 'object'
        assert df['Timestamp'].iloc[0] == '2023-01-01 06:00'

    def test_load_csv_data_types(self, temp_csv_file):
        """Test that data types are appropriate"""
        df = load_csv(temp_csv_file)

        # Numeric columns should be numeric
        numeric_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'Tamb', 'RH', 'WS',
                       'WSgust', 'WSstdev', 'WD', 'WDstdev', 'BP', 'Precipitation', 'TModA', 'TModB']
        for col in numeric_cols:
            assert pd.api.types.is_numeric_dtype(df[col])

        # Integer columns
        int_cols = ['GHI', 'DNI', 'DHI', 'Cleaning']
        for col in int_cols:
            assert pd.api.types.is_integer_dtype(df[col])

        # Float columns
        float_cols = ['ModA', 'ModB', 'Tamb', 'RH', 'WS', 'WSgust', 'WSstdev',
                     'WD', 'WDstdev', 'BP', 'Precipitation', 'TModA', 'TModB']
        for col in float_cols:
            assert pd.api.types.is_float_dtype(df[col])

    def test_load_country_files(self, tmp_path, sample_csv_data):
        """Test loading multiple country files"""
        # Create temporary files for different countries
        benin_file = tmp_path / "benin.csv"
        togo_file = tmp_path / "togo.csv"

        benin_file.write_text(sample_csv_data)
        togo_file.write_text(sample_csv_data)

        file_map = {
            "Benin": str(benin_file),
            "Togo": str(togo_file)
        }

        result = load_country_files(file_map)

        # Check result structure
        assert isinstance(result, dict)
        assert set(result.keys()) == {"Benin", "Togo"}

        # Check each dataframe
        for country, df in result.items():
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 4
            assert pd.api.types.is_datetime64_any_dtype(df['Timestamp'])

    def test_load_country_files_empty_map(self):
        """Test loading with empty file map"""
        result = load_country_files({})
        assert result == {}

    def test_load_csv_file_not_found(self):
        """Test error handling for non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_csv("non_existent_file.csv")

    def test_load_country_files_missing_file(self, tmp_path):
        """Test error handling when a file in the map doesn't exist"""
        file_map = {
            "Benin": str(tmp_path / "benin.csv"),
            "Togo": str(tmp_path / "togo.csv")
        }

        with pytest.raises(FileNotFoundError):
            load_country_files(file_map)