import pytest
import pandas as pd
import numpy as np
from scripts.transform import fill_interpolate, add_daily_aggregates, add_post_clean_flag


class TestDataTransformation:
    """Test suite for data transformation functions"""

    @pytest.fixture
    def sample_dataframe_with_gaps(self):
        """Create a sample dataframe with missing values and gaps"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 18:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': [0, 100, np.nan, 300, 400, np.nan, np.nan, 700, 800, 900, 1000, 1100, 1200],
            'DNI': [0, 80, 160, np.nan, 320, 400, 480, np.nan, 640, 720, 800, 880, 960],
            'DHI': [0, 20, 40, 60, np.nan, 100, 120, 140, np.nan, 180, 200, 220, 240],
            'ModA': [0.0, 95.0, np.nan, 285.0, 380.0, np.nan, np.nan, 665.0, 760.0, 855.0, 950.0, 1045.0, 1140.0],
            'Tamb': [25.0, 25.5, 26.0, 26.5, 27.0, np.nan, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def sample_daily_dataframe(self):
        """Create a sample dataframe for daily aggregation testing"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-03 18:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': np.random.uniform(200, 600, len(timestamps)),
            'DNI': np.random.uniform(150, 500, len(timestamps)),
            'DHI': np.random.uniform(50, 150, len(timestamps)),
            'ModA': np.random.uniform(180, 550, len(timestamps)),
            'ModB': np.random.uniform(185, 555, len(timestamps)),
            'Tamb': np.random.uniform(20, 35, len(timestamps)),
            'RH': np.random.uniform(40, 80, len(timestamps)),
            'WS': np.random.uniform(1, 8, len(timestamps)),
            'BP': np.random.uniform(1000, 1020, len(timestamps))
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def sample_cleaning_dataframe(self):
        """Create a sample dataframe with cleaning events"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-05 18:00', freq='H')
        n_points = len(timestamps)
        data = {
            'Timestamp': timestamps,
            'GHI': np.random.uniform(200, 600, n_points),
            'Cleaning': [0]*20 + [1] + [0]*43 + [1] + [0]*44  # Two cleaning events
        }
        return pd.DataFrame(data)

    def test_fill_interpolate_basic(self, sample_dataframe_with_gaps):
        """Test basic interpolation functionality"""
        original_missing = sample_dataframe_with_gaps.isnull().sum().sum()
        result = fill_interpolate(sample_dataframe_with_gaps)

        # Check that result is a DataFrame
        assert isinstance(result, pd.DataFrame)

        # Check that missing values have been filled
        result_missing = result.isnull().sum().sum()
        assert result_missing < original_missing

        # Check that Timestamp column is preserved
        assert 'Timestamp' in result.columns
        assert pd.api.types.is_datetime64_any_dtype(result['Timestamp'])

    def test_fill_interpolate_no_missing_values(self):
        """Test interpolation when no missing values exist"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 12:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': [0, 100, 200, 300, 400, 500, 600],
            'DNI': [0, 80, 160, 240, 320, 400, 480]
        }
        df = pd.DataFrame(data)

        result = fill_interpolate(df)

        # Should be identical to original
        pd.testing.assert_frame_equal(result, df)

    def test_fill_interpolate_all_missing_column(self):
        """Test interpolation when entire column is missing"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 12:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': [0, 100, 200, 300, 400, 500, 600],
            'DNI': [np.nan] * 7  # All missing
        }
        df = pd.DataFrame(data)

        result = fill_interpolate(df)

        # DNI column should still be all NaN (can't interpolate all missing)
        assert result['DNI'].isnull().all()

    def test_fill_interpolate_preserves_non_numeric(self):
        """Test that non-numeric columns are preserved"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 12:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': [0, 100, 200, 300, 400, 500, 600],
            'Comments': ['Good', 'Bad', 'Good', 'Bad', 'Good', 'Bad', 'Good']
        }
        df = pd.DataFrame(data)

        result = fill_interpolate(df)

        # Comments column should be unchanged
        pd.testing.assert_series_equal(result['Comments'], df['Comments'])

    def test_fill_interpolate_method_parameter(self, sample_dataframe_with_gaps):
        """Test different interpolation methods"""
        result_linear = fill_interpolate(sample_dataframe_with_gaps, method='linear')
        result_time = fill_interpolate(sample_dataframe_with_gaps, method='time')

        # Both should fill missing values
        assert result_linear.isnull().sum().sum() < sample_dataframe_with_gaps.isnull().sum().sum()
        assert result_time.isnull().sum().sum() < sample_dataframe_with_gaps.isnull().sum().sum()

    def test_add_daily_aggregates_basic(self, sample_daily_dataframe):
        """Test basic daily aggregation functionality"""
        result = add_daily_aggregates(sample_daily_dataframe)

        # Check result structure
        assert isinstance(result, pd.DataFrame)
        assert 'Date' in result.columns

        # Check that we have daily aggregations
        expected_columns = ['Date', 'GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'Tamb', 'RH', 'WS', 'BP']
        for col in expected_columns:
            assert col in result.columns

        # Should have 3 days of data
        assert len(result) == 3

    def test_add_daily_aggregates_missing_columns(self):
        """Test daily aggregation with missing columns"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-02 18:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': np.random.uniform(200, 600, len(timestamps)),
            'DNI': np.random.uniform(150, 500, len(timestamps))
            # Missing other columns
        }
        df = pd.DataFrame(data)

        with pytest.raises(KeyError):
            add_daily_aggregates(df)

    def test_add_daily_aggregates_single_day(self):
        """Test daily aggregation with single day data"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 18:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200],
            'DNI': [0, 80, 160, 240, 320, 400, 480, 560, 640, 720, 800, 880, 960],
            'DHI': [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240],
            'ModA': [0.0, 95.0, 190.0, 285.0, 380.0, 475.0, 570.0, 665.0, 760.0, 855.0, 950.0, 1045.0, 1140.0],
            'ModB': [0.0, 98.0, 196.0, 294.0, 392.0, 490.0, 588.0, 686.0, 784.0, 882.0, 980.0, 1078.0, 1176.0],
            'Tamb': [25.0, 25.5, 26.0, 26.5, 27.0, 27.5, 28.0, 28.5, 29.0, 29.5, 30.0, 30.5, 31.0],
            'RH': [60.0, 58.0, 56.0, 54.0, 52.0, 50.0, 48.0, 46.0, 44.0, 42.0, 40.0, 38.0, 36.0],
            'WS': [2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2],
            'BP': [1013.0, 1013.1, 1013.2, 1013.3, 1013.4, 1013.5, 1013.6, 1013.7, 1013.8, 1013.9, 1014.0, 1014.1, 1014.2]
        }
        df = pd.DataFrame(data)

        result = add_daily_aggregates(df)

        # Should have 1 day of data
        assert len(result) == 1
        assert result['Date'].iloc[0] == pd.Timestamp('2023-01-01').date()

        # Check that averages are calculated correctly
        assert result['GHI'].iloc[0] == df['GHI'].mean()
        assert result['DNI'].iloc[0] == df['DNI'].mean()

    def test_add_post_clean_flag_basic(self, sample_cleaning_dataframe):
        """Test basic post-cleaning flag functionality"""
        result = add_post_clean_flag(sample_cleaning_dataframe)

        # Check that post_clean column is added
        assert 'post_clean' in result.columns

        # Check that it's boolean
        assert result['post_clean'].dtype == bool

    def test_add_post_clean_flag_no_cleaning_events(self):
        """Test post-clean flag when no cleaning events exist"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 18:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': np.random.uniform(200, 600, len(timestamps)),
            'Cleaning': [0] * len(timestamps)  # No cleaning events
        }
        df = pd.DataFrame(data)

        result = add_post_clean_flag(df)

        # All post_clean flags should be False
        assert not result['post_clean'].any()

    def test_add_post_clean_flag_custom_days(self, sample_cleaning_dataframe):
        """Test post-clean flag with custom days_after parameter"""
        result_1day = add_post_clean_flag(sample_cleaning_dataframe, days_after=1)
        result_2days = add_post_clean_flag(sample_cleaning_dataframe, days_after=2)

        # More days should result in more True flags
        assert result_2days['post_clean'].sum() >= result_1day['post_clean'].sum()

    def test_add_post_clean_flag_missing_cleaning_column(self):
        """Test post-clean flag when Cleaning column is missing"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 12:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': [100, 200, 300, 400, 500, 600, 700]  # Match the length
        }
        df = pd.DataFrame(data)

        result = add_post_clean_flag(df)

        # Should handle missing Cleaning column gracefully (treat as all zeros)
        assert 'post_clean' in result.columns
        assert not result['post_clean'].any()

    def test_add_post_clean_flag_null_cleaning_values(self):
        """Test post-clean flag with null values in Cleaning column"""
        timestamps = pd.date_range('2023-01-01 06:00', '2023-01-01 12:00', freq='H')
        data = {
            'Timestamp': timestamps,
            'GHI': [100, 200, 300, 400, 500, 600, 700],  # Match the length
            'Cleaning': [0, np.nan, 1, 0, np.nan, 0, 0]  # Mixed nulls
        }
        df = pd.DataFrame(data)

        result = add_post_clean_flag(df)

        # Should handle nulls by treating them as 0
        assert 'post_clean' in result.columns
        assert result['post_clean'].dtype == bool

    def test_add_post_clean_flag_preserves_other_columns(self, sample_cleaning_dataframe):
        """Test that other columns are preserved"""
        original_columns = set(sample_cleaning_dataframe.columns)
        result = add_post_clean_flag(sample_cleaning_dataframe)

        # Should have original columns plus post_clean
        assert set(result.columns) == original_columns | {'post_clean'}

        # Original data should be preserved
        for col in original_columns:
            pd.testing.assert_series_equal(result[col], sample_cleaning_dataframe[col])