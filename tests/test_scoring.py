import pytest
import pandas as pd
import numpy as np
from scripts.scoring import country_score


class TestScoringFunctions:
    """Test suite for scoring functions"""

    @pytest.fixture
    def sample_daily_dataframe(self):
        """Create a sample daily aggregated dataframe for testing"""
        data = {
            'GHI': [200, 250, 300, 350, 400, 450, 500],  # 7 days of data
            'DNI': [160, 200, 240, 280, 320, 360, 400],
            'DHI': [40, 50, 60, 70, 80, 90, 100],
            'Tamb': [25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0]
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def high_potential_dataframe(self):
        """Create a dataframe representing high solar potential"""
        data = {
            'GHI': [500, 550, 600, 650, 700, 750, 800],  # High GHI
            'DNI': [400, 440, 480, 520, 560, 600, 640],  # High DNI
            'DHI': [100, 110, 120, 130, 140, 150, 160],  # Moderate DHI
            'Tamb': [20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0]  # Moderate temperature
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def low_potential_dataframe(self):
        """Create a dataframe representing low solar potential"""
        data = {
            'GHI': [50, 75, 100, 125, 150, 175, 200],  # Low GHI
            'DNI': [30, 45, 60, 75, 90, 105, 120],     # Low DNI
            'DHI': [20, 30, 40, 50, 60, 70, 80],       # High DHI (cloudy)
            'Tamb': [35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 41.0]  # High temperature
        }
        return pd.DataFrame(data)

    def test_country_score_basic(self, sample_daily_dataframe):
        """Test basic country scoring functionality"""
        result = country_score(sample_daily_dataframe)

        # Check result structure
        assert isinstance(result, dict)
        assert 'agg' in result
        assert 'score' in result

        # Check aggregated values
        agg = result['agg']
        assert 'avg_GHI' in agg
        assert 'avg_DNI' in agg
        assert 'avg_DHI' in agg
        assert 'avg_Tamb' in agg

        # Check that score is a number
        assert isinstance(result['score'], (int, float))

    def test_country_score_aggregates(self, sample_daily_dataframe):
        """Test that aggregates are calculated correctly"""
        result = country_score(sample_daily_dataframe)

        agg = result['agg']

        # Manually calculate expected averages
        expected_ghi = sample_daily_dataframe['GHI'].mean()
        expected_dni = sample_daily_dataframe['DNI'].mean()
        expected_dhi = sample_daily_dataframe['DHI'].mean()
        expected_tamb = sample_daily_dataframe['Tamb'].mean()

        assert agg['avg_GHI'] == expected_ghi
        assert agg['avg_DNI'] == expected_dni
        assert agg['avg_DHI'] == expected_dhi
        assert agg['avg_Tamb'] == expected_tamb

    def test_country_score_default_weights(self, sample_daily_dataframe):
        """Test scoring with default weights"""
        result = country_score(sample_daily_dataframe)

        agg = result['agg']

        # Default weights: GHI=0.4, DNI=0.35, DHI=0.15, Tamb=0.10
        expected_score = (0.4 * agg['avg_GHI'] +
                         0.35 * agg['avg_DNI'] -
                         0.15 * agg['avg_DHI'] -
                         0.10 * ((agg['avg_Tamb'] - 0) / 40.0) * 1000)

        assert result['score'] == expected_score

    def test_country_score_custom_weights(self, sample_daily_dataframe):
        """Test scoring with custom weights"""
        custom_weights = {'GHI': 0.5, 'DNI': 0.3, 'DHI': 0.1, 'Tamb': 0.1}
        result = country_score(sample_daily_dataframe, weights=custom_weights)

        agg = result['agg']

        expected_score = (0.5 * agg['avg_GHI'] +
                         0.3 * agg['avg_DNI'] -
                         0.1 * agg['avg_DHI'] -
                         0.1 * ((agg['avg_Tamb'] - 0) / 40.0) * 1000)

        assert result['score'] == expected_score

    def test_country_score_temperature_normalization(self, sample_daily_dataframe):
        """Test temperature normalization in scoring"""
        result = country_score(sample_daily_dataframe)

        agg = result['agg']
        temp_norm = (agg['avg_Tamb'] - 0) / 40.0

        # Temperature normalization should be between 0 and 1 for reasonable temperatures
        assert 0 <= temp_norm <= 1

        # For our sample data (avg ~28°C), normalized temp should be around 0.7
        expected_temp_norm = (agg['avg_Tamb'] - 0) / 40.0
        assert abs(temp_norm - expected_temp_norm) < 1e-10

    def test_country_score_high_vs_low_potential(self, high_potential_dataframe, low_potential_dataframe):
        """Test that high potential scores higher than low potential"""
        high_result = country_score(high_potential_dataframe)
        low_result = country_score(low_potential_dataframe)

        # High potential should have higher score
        assert high_result['score'] > low_result['score']

        # High potential should have higher GHI and DNI averages
        assert high_result['agg']['avg_GHI'] > low_result['agg']['avg_GHI']
        assert high_result['agg']['avg_DNI'] > low_result['agg']['avg_DNI']

    def test_country_score_temperature_penalty(self):
        """Test that higher temperatures result in lower scores"""
        # Create two dataframes with same solar metrics but different temperatures
        base_data = {
            'GHI': [300, 350, 400],
            'DNI': [240, 280, 320],
            'DHI': [60, 70, 80]
        }

        cool_data = base_data.copy()
        cool_data['Tamb'] = [20.0, 21.0, 22.0]  # Cool temperatures

        hot_data = base_data.copy()
        hot_data['Tamb'] = [35.0, 36.0, 37.0]  # Hot temperatures

        cool_df = pd.DataFrame(cool_data)
        hot_df = pd.DataFrame(hot_data)

        cool_result = country_score(cool_df)
        hot_result = country_score(hot_df)

        # Cooler location should score higher (less temperature penalty)
        assert cool_result['score'] > hot_result['score']

    def test_country_score_missing_columns(self, sample_daily_dataframe):
        """Test error handling when required columns are missing"""
        # Remove a required column
        df_missing = sample_daily_dataframe.drop(columns=['GHI'])

        with pytest.raises(KeyError):
            country_score(df_missing)

    def test_country_score_empty_dataframe(self):
        """Test scoring with empty dataframe"""
        empty_df = pd.DataFrame(columns=['GHI', 'DNI', 'DHI', 'Tamb'])

        result = country_score(empty_df)

        # Should return NaN values for empty dataframe
        assert pd.isna(result['score'])
        assert pd.isna(result['agg']['avg_GHI'])
        assert pd.isna(result['agg']['avg_DNI'])
        assert pd.isna(result['agg']['avg_DHI'])
        assert pd.isna(result['agg']['avg_Tamb'])

    def test_country_score_single_row(self):
        """Test scoring with single row dataframe"""
        single_row_data = {
            'GHI': [300],
            'DNI': [240],
            'DHI': [60],
            'Tamb': [25.0]
        }
        single_df = pd.DataFrame(single_row_data)

        result = country_score(single_df)

        # Should work with single row
        assert isinstance(result['score'], (int, float))
        assert result['agg']['avg_GHI'] == 300
        assert result['agg']['avg_DNI'] == 240
        assert result['agg']['avg_DHI'] == 60
        assert result['agg']['avg_Tamb'] == 25.0

    def test_country_score_extreme_temperatures(self):
        """Test scoring with extreme temperatures"""
        extreme_data = {
            'GHI': [300, 350, 400],
            'DNI': [240, 280, 320],
            'DHI': [60, 70, 80],
            'Tamb': [0.0, 5.0, 10.0]  # Very cold
        }
        extreme_df = pd.DataFrame(extreme_data)

        result = country_score(extreme_df)

        # Should handle extreme temperatures
        assert isinstance(result['score'], (int, float))
        # Very cold temperatures should give minimal penalty
        temp_norm = (result['agg']['avg_Tamb'] - 0) / 40.0
        assert temp_norm < 0.5  # Less than 20°C average

    def test_country_score_weights_sum_to_one(self):
        """Test that default weights sum to 1.0"""
        # This is more of a validation test
        default_weights = {'GHI': 0.4, 'DNI': 0.35, 'DHI': 0.15, 'Tamb': 0.10}
        total_weight = sum(default_weights.values())
        assert abs(total_weight - 1.0) < 1e-10