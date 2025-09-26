import pytest
import pandas as pd
import numpy as np
from scripts.qa import basic_quality_report, drop_bad_timestamps


class TestQualityAssessment:
    """Test suite for quality assessment functions"""

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample dataframe for testing"""
        data = {
            'Timestamp': pd.date_range('2023-01-01', periods=10, freq='H'),
            'GHI': [0, 100, 200, 300, 400, 500, 600, 700, 800, 900],
            'DNI': [0, 80, 160, 240, 320, 400, 480, 560, 640, 720],
            'DHI': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180],
            'ModA': [0.0, 95.0, 190.0, 285.0, 380.0, 475.0, 570.0, 665.0, 760.0, 855.0],
            'ModB': [0.0, 98.0, 196.0, 294.0, 392.0, 490.0, 588.0, 686.0, 784.0, 882.0],
            'Tamb': [25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5],
            'RH': [60.0, 58.0, 56.0, 54.0, 52.0, 50.0, 48.0, 46.0, 44.0, 42.0],
            'WS': [2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9],
            'WSgust': [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9],
            'Precipitation': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'Comments': [None, None, None, None, None, None, None, None, None, None]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def dataframe_with_issues(self):
        """Create a dataframe with quality issues for testing"""
        data = {
            'Timestamp': pd.date_range('2023-01-01', periods=10, freq='H'),
            'GHI': [0, 100, 200, -50, 400, 500, np.nan, 700, 800, 900],  # negative and NaN
            'DNI': [0, 80, 160, 240, 320, 400, 480, 560, 640, 720],
            'DHI': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180],
            'ModA': [0.0, 95.0, 190.0, 285.0, np.nan, 475.0, 570.0, 665.0, 760.0, 855.0],  # NaN
            'ModB': [0.0, 98.0, 196.0, 294.0, 392.0, 490.0, 588.0, 686.0, 784.0, 882.0],
            'Tamb': [25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5],
            'RH': [60.0, 58.0, 56.0, 54.0, 52.0, 50.0, 48.0, 46.0, 44.0, 42.0],
            'WS': [2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9],
            'WSgust': [-1.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9],  # negative
            'Precipitation': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            'Comments': ['Good', None, None, 'Issue', None, None, None, None, None, None]
        }
        return pd.DataFrame(data)

    def test_basic_quality_report_structure(self, sample_dataframe):
        """Test that basic_quality_report returns expected structure"""
        report = basic_quality_report(sample_dataframe)

        # Check required keys
        required_keys = ['n_rows', 'n_cols', 'missing_per_col', 'dtypes', 'negative_counts', 'duplicate_rows']
        for key in required_keys:
            assert key in report

    def test_basic_quality_report_counts(self, sample_dataframe):
        """Test that counts are correct"""
        report = basic_quality_report(sample_dataframe)

        assert report['n_rows'] == 10
        assert report['n_cols'] == 12  # All columns
        assert report['duplicate_rows'] == 0  # No duplicates in sample

    def test_basic_quality_report_missing_values(self, sample_dataframe):
        """Test missing value detection"""
        report = basic_quality_report(sample_dataframe)

        # Comments column has None values (10 missing)
        assert report['missing_per_col']['Comments'] == 10

        # Other columns should have no missing values
        for col, missing_count in report['missing_per_col'].items():
            if col != 'Comments':
                assert missing_count == 0

    def test_basic_quality_report_negative_counts(self, sample_dataframe):
        """Test negative value detection for clean data"""
        report = basic_quality_report(sample_dataframe)

        # Sample dataframe has no negative values
        non_negative_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'Precipitation', 'WS', 'WSgust']
        for col in non_negative_cols:
            assert report['negative_counts'][col] == 0

    def test_basic_quality_report_with_issues(self, dataframe_with_issues):
        """Test quality report with problematic data"""
        report = basic_quality_report(dataframe_with_issues)

        # Check missing values
        assert report['missing_per_col']['GHI'] == 1  # One NaN in GHI
        assert report['missing_per_col']['ModA'] == 1  # One NaN in ModA

        # Check negative values
        assert report['negative_counts']['GHI'] == 1  # One negative in GHI
        assert report['negative_counts']['WSgust'] == 1  # One negative in WSgust

        # Check duplicates (should be 0)
        assert report['duplicate_rows'] == 0

    def test_basic_quality_report_dtypes(self, sample_dataframe):
        """Test data type reporting"""
        report = basic_quality_report(sample_dataframe)

        # Check some expected dtypes
        assert 'datetime64[ns]' in report['dtypes']['Timestamp']
        assert 'int64' in report['dtypes']['GHI']
        assert 'int64' in report['dtypes']['DNI']

    def test_drop_bad_timestamps_no_timestamp_column(self):
        """Test drop_bad_timestamps when no Timestamp column exists"""
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        result = drop_bad_timestamps(df)

        pd.testing.assert_frame_equal(result, df)

    def test_drop_bad_timestamps_clean_timestamps(self, sample_dataframe):
        """Test drop_bad_timestamps with clean timestamp data"""
        original_len = len(sample_dataframe)
        result = drop_bad_timestamps(sample_dataframe)

        assert len(result) == original_len
        pd.testing.assert_frame_equal(result, sample_dataframe)

    def test_drop_bad_timestamps_with_nulls(self):
        """Test drop_bad_timestamps with null timestamps"""
        data = {
            'Timestamp': [pd.Timestamp('2023-01-01'), None, pd.Timestamp('2023-01-03'), None],
            'GHI': [100, 200, 300, 400]
        }
        df = pd.DataFrame(data)

        result = drop_bad_timestamps(df)

        assert len(result) == 2
        assert result['GHI'].tolist() == [100, 300]
        assert pd.notna(result['Timestamp']).all()

    def test_drop_bad_timestamps_all_null(self):
        """Test drop_bad_timestamps when all timestamps are null"""
        data = {
            'Timestamp': [None, None, None],
            'GHI': [100, 200, 300]
        }
        df = pd.DataFrame(data)

        result = drop_bad_timestamps(df)

        assert len(result) == 0
        assert list(result.columns) == ['Timestamp', 'GHI']

    def test_drop_bad_timestamps_preserves_other_columns(self):
        """Test that other columns are preserved when dropping bad timestamps"""
        data = {
            'Timestamp': [pd.Timestamp('2023-01-01'), None, pd.Timestamp('2023-01-03')],
            'GHI': [100, 200, 300],
            'DNI': [80, 160, 240],
            'Comments': ['Good', 'Bad', 'Good']
        }
        df = pd.DataFrame(data)

        result = drop_bad_timestamps(df)

        expected_data = {
            'Timestamp': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-03')],
            'GHI': [100, 300],
            'DNI': [80, 240],
            'Comments': ['Good', 'Good']
        }
        expected = pd.DataFrame(expected_data)

        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected.reset_index(drop=True))