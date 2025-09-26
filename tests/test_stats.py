import pytest
import pandas as pd
import numpy as np
from scripts.stats import compute_zscore, flag_outliers_z, cleaning_impact_test


class TestStatisticalFunctions:
    """Test suite for statistical functions"""

    @pytest.fixture
    def sample_series(self):
        """Create a sample pandas Series for testing"""
        return pd.Series([1, 2, 3, 4, 5])

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample dataframe for testing"""
        data = {
            'Timestamp': pd.date_range('2023-01-01', periods=20, freq='H'),
            'GHI': [100, 105, 110, 115, 120, 125, 130, 135, 140, 145,
                   2000, 155, 160, 165, 170, 175, 180, 185, 190, 195],  # 2000 is outlier
            'ModA': [95, 100, 105, 110, 115, 120, 125, 130, 135, 140,
                    1950, 150, 155, 160, 165, 170, 175, 180, 185, 190],  # 1950 is outlier
            'Cleaning': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0,  # Cleaning event at index 5
                        0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        return pd.DataFrame(data)

    def test_compute_zscore_basic(self, sample_series):
        """Test basic z-score computation"""
        z_scores = compute_zscore(sample_series)

        # Check that result is a pandas Series
        assert isinstance(z_scores, pd.Series)

        # Check that mean is approximately 0
        assert abs(z_scores.mean()) < 1e-10

        # Check that standard deviation is 1 (z-scores are normalized)
        assert abs(z_scores.std(ddof=0) - 1.0) < 1e-10

        # Check specific values for series [1,2,3,4,5]
        # mean = 3, std = sqrt(2) ≈ 1.414
        expected_z = np.array([-1.41421356, -0.70710678, 0.0, 0.70710678, 1.41421356])
        np.testing.assert_allclose(z_scores.values, expected_z, rtol=1e-6)

    def test_compute_zscore_single_value(self):
        """Test z-score computation with single value (should return NaN)"""
        series = pd.Series([5])
        z_scores = compute_zscore(series)

        assert pd.isna(z_scores.iloc[0])

    def test_compute_zscore_constant_values(self):
        """Test z-score computation with constant values (should return NaN)"""
        series = pd.Series([5, 5, 5, 5, 5])
        z_scores = compute_zscore(series)

        assert all(pd.isna(z_scores))

    def test_compute_zscore_with_nan(self):
        """Test z-score computation with NaN values"""
        series = pd.Series([1, 2, np.nan, 4, 5])
        z_scores = compute_zscore(series)

        # NaN should be preserved
        assert pd.isna(z_scores.iloc[2])

        # Other values should be computed correctly
        assert not pd.isna(z_scores.iloc[0])
        assert not pd.isna(z_scores.iloc[1])
        assert not pd.isna(z_scores.iloc[3])
        assert not pd.isna(z_scores.iloc[4])

    def test_flag_outliers_z_basic(self, sample_dataframe):
        """Test basic outlier flagging functionality"""
        df = sample_dataframe.copy()
        result = flag_outliers_z(df, 'GHI', threshold=2.0)

        # Check that new columns are added
        assert 'GHI_z' in result.columns
        assert 'GHI_outlier' in result.columns

        # Check that z-scores are computed
        assert isinstance(result['GHI_z'], pd.Series)
        assert abs(result['GHI_z'].mean()) < 1e-10  # Mean should be ~0

        # Check that outliers are flagged
        assert result['GHI_outlier'].sum() > 0  # Should have outliers

    def test_flag_outliers_z_threshold(self, sample_dataframe):
        """Test outlier flagging with different thresholds"""
        df = sample_dataframe.copy()

        # Test with threshold 3.0 (stricter)
        result_strict = flag_outliers_z(df, 'GHI', threshold=3.0)

        # Test with threshold 1.0 (looser)
        result_loose = flag_outliers_z(df, 'GHI', threshold=1.0)

        # Looser threshold should catch more outliers
        assert result_loose['GHI_outlier'].sum() >= result_strict['GHI_outlier'].sum()

    def test_flag_outliers_z_no_outliers(self):
        """Test outlier flagging when no outliers exist"""
        # Create data with no outliers
        data = {'GHI': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]}
        df = pd.DataFrame(data)

        result = flag_outliers_z(df, 'GHI', threshold=3.0)

        # Should have no outliers flagged
        assert result['GHI_outlier'].sum() == 0

    def test_flag_outliers_z_column_not_found(self, sample_dataframe):
        """Test error handling when column doesn't exist"""
        df = sample_dataframe.copy()

        with pytest.raises(KeyError):
            flag_outliers_z(df, 'NonExistentColumn')

    def test_cleaning_impact_test_basic(self, sample_dataframe):
        """Test basic cleaning impact analysis"""
        # The sample_dataframe has only 1 cleaning event, so it should return the "not enough events" message
        result = cleaning_impact_test(sample_dataframe, metric='ModA', pre_window_hours=1, post_window_hours=1)

        assert result['n_events'] == 1
        assert 'message' in result
        assert result['message'] == "Not enough paired events for a t-test"

    def test_cleaning_impact_test_no_events(self):
        """Test cleaning impact when no cleaning events exist"""
        data = {
            'Timestamp': pd.date_range('2023-01-01', periods=10, freq='H'),
            'ModA': [100, 105, 110, 115, 120, 125, 130, 135, 140, 145],
            'Cleaning': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # No cleaning events
        }
        df = pd.DataFrame(data)

        result = cleaning_impact_test(df, metric='ModA')

        assert result['n_events'] == 0
        assert 'message' in result
        assert result['message'] == "Not enough paired events for a t-test"

    def test_cleaning_impact_test_insufficient_events(self):
        """Test cleaning impact with only one cleaning event"""
        data = {
            'Timestamp': pd.date_range('2023-01-01', periods=5, freq='H'),
            'ModA': [100, 105, 110, 115, 120],
            'Cleaning': [0, 0, 1, 0, 0]  # One cleaning event
        }
        df = pd.DataFrame(data)

        result = cleaning_impact_test(df, metric='ModA', pre_window_hours=1, post_window_hours=1)

        # With 1 event, should return "not enough events" message
        assert result['n_events'] == 1
        assert 'message' in result
        assert result['message'] == "Not enough paired events for a t-test"

    def test_cleaning_impact_test_multiple_events(self):
        """Test cleaning impact with multiple cleaning events"""
        data = {
            'Timestamp': pd.date_range('2023-01-01', periods=50, freq='H'),
            'ModA': list(range(100, 150)),  # Increasing values
            'Cleaning': [0]*10 + [1] + [0]*9 + [1] + [0]*29  # Two cleaning events
        }
        df = pd.DataFrame(data)

        result = cleaning_impact_test(df, metric='ModA')

        assert result['n_events'] == 2
        assert 't_stat' in result
        assert 'p_value' in result

    def test_cleaning_impact_test_different_metric(self, sample_dataframe):
        """Test cleaning impact with different metric"""
        result = cleaning_impact_test(sample_dataframe, metric='GHI', pre_window_hours=1, post_window_hours=1)

        assert result['n_events'] == 1
        assert 'message' in result
        assert result['message'] == "Not enough paired events for a t-test"

    def test_cleaning_impact_test_custom_windows(self, sample_dataframe):
        """Test cleaning impact with custom time windows"""
        result = cleaning_impact_test(sample_dataframe, metric='ModA',
                                    pre_window_hours=1, post_window_hours=1)

        assert result['n_events'] == 1
        assert 'message' in result
        assert result['message'] == "Not enough paired events for a t-test"

    def test_cleaning_impact_test_no_timestamp_column(self):
        """Test cleaning impact when no Timestamp column exists"""
        data = {
            'ModA': [100, 105, 110, 115, 120],
            'Cleaning': [0, 0, 1, 0, 0]
        }
        df = pd.DataFrame(data)

        with pytest.raises(KeyError):
            cleaning_impact_test(df, metric='ModA')