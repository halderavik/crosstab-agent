"""
Cross-tabulation engine for analyzing relationships between variables.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field, ConfigDict
from scipy import stats
from dataclasses import dataclass
from enum import Enum
from scipy.stats import chi2_contingency
from core.crosstab_result import CrosstabResult, CrosstabStatistics

class StatisticType(Enum):
    """Types of statistical tests available."""
    CHI_SQUARE = "chi_square"
    FISHER_EXACT = "fisher_exact"
    T_TEST = "t_test"
    ANOVA = "anova"

@dataclass
class StatisticalResult:
    """Results of a statistical test."""
    test_type: StatisticType
    statistic: float
    p_value: float
    degrees_of_freedom: Optional[int] = None
    effect_size: Optional[float] = None

class CrosstabGenerator:
    """Generates cross-tabulations with various statistics."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize the cross-tabulation generator.
        
        Args:
            data: Input DataFrame
        """
        self.data = data
    
    def generate(
        self,
        row_var: str,
        col_var: str,
        include_percentages: bool = True,
        include_statistics: bool = True
    ) -> CrosstabResult:
        """Generate a cross-tabulation.
        
        Args:
            row_var: Row variable name
            col_var: Column variable name
            include_percentages: Whether to include percentage calculations
            include_statistics: Whether to include statistical tests
            
        Returns:
            CrosstabResult object containing the analysis
        """
        # Create the contingency table
        table = pd.crosstab(
            self.data[row_var],
            self.data[col_var],
            margins=True
        )
        
        result = {
            'table': table,
            'row_percentages': self._calculate_row_percentages(table),
            'column_percentages': self._calculate_column_percentages(table),
            'total_percentages': self._calculate_total_percentages(table),
            'statistics': self._calculate_statistics(table) if include_statistics else {},
            'expected_values': None,
            'residuals': None
        }
        
        if include_statistics:
            result['expected_values'] = self._calculate_expected_values(table)
            result['residuals'] = self._calculate_residuals(
                table,
                result['expected_values']
            )
        
        return CrosstabResult(**result)
    
    def _calculate_row_percentages(self, table: pd.DataFrame) -> pd.DataFrame:
        """Calculate row percentages."""
        return table.div(table.sum(axis=1), axis=0) * 100
    
    def _calculate_column_percentages(self, table: pd.DataFrame) -> pd.DataFrame:
        """Calculate column percentages."""
        return table.div(table.sum(axis=0), axis=1) * 100
    
    def _calculate_total_percentages(self, table: pd.DataFrame) -> pd.DataFrame:
        """Calculate percentages of total."""
        total = table.sum().sum()
        return table / total * 100
    
    def _calculate_statistics(self, table: pd.DataFrame) -> Dict[str, float]:
        """Calculate statistical measures."""
        # Remove margins for statistical calculations
        table_no_margins = table.iloc[:-1, :-1]
        
        # Chi-square test
        chi2, p_value, dof, expected = chi2_contingency(table_no_margins)
        
        # Cramer's V
        n = table_no_margins.sum().sum()
        min_dim = min(table_no_margins.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim))
        
        return {
            'chi_square': chi2,
            'p_value': p_value,
            'degrees_of_freedom': dof,
            'cramers_v': cramers_v
        }
    
    def _calculate_expected_values(self, table: pd.DataFrame) -> pd.DataFrame:
        """Calculate expected values."""
        table_no_margins = table.iloc[:-1, :-1]
        _, _, _, expected = chi2_contingency(table_no_margins)
        return pd.DataFrame(
            expected,
            index=table_no_margins.index,
            columns=table_no_margins.columns
        )
    
    def _calculate_residuals(
        self,
        observed: pd.DataFrame,
        expected: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate standardized residuals."""
        observed_no_margins = observed.iloc[:-1, :-1]
        residuals = (observed_no_margins - expected) / np.sqrt(expected)
        return residuals

class BannerTableGenerator:
    """Generates banner tables for cross-tabulation analysis."""
    
    def __init__(self, data: pd.DataFrame):
        """Initialize the banner table generator.
        
        Args:
            data: Input DataFrame
        """
        self.data = data
        self.generator = CrosstabGenerator(data)
    
    def generate_banner(
        self,
        row_vars: List[str],
        col_vars: List[str],
        include_percentages: bool = True,
        include_statistics: bool = True
    ) -> Dict[str, CrosstabResult]:
        """Generate a banner table.
        
        Args:
            row_vars: List of row variable names
            col_vars: List of column variable names
            include_percentages: Whether to include percentage calculations
            include_statistics: Whether to include statistical tests
            
        Returns:
            Dictionary mapping variable pairs to their CrosstabResult
        """
        results = {}
        
        for row_var in row_vars:
            for col_var in col_vars:
                key = f"{row_var}_by_{col_var}"
                results[key] = self.generator.generate(
                    row_var,
                    col_var,
                    include_percentages,
                    include_statistics
                )
        
        return results
    
    def combine_banner_results(
        self,
        results: Dict[str, CrosstabResult]
    ) -> pd.DataFrame:
        """Combine multiple cross-tabulation results into a banner table.
        
        Args:
            results: Dictionary of CrosstabResults
            
        Returns:
            Combined banner table as DataFrame
        """
        tables = []
        
        for key, result in results.items():
            # Add variable name as column prefix
            table = result.table.copy()
            table.columns = [f"{key}_{col}" for col in table.columns]
            tables.append(table)
        
        # Combine all tables horizontally
        return pd.concat(tables, axis=1)

class CrosstabEngine:
    """
    Engine for performing cross-tabulations and statistical analysis.
    
    This class provides functionality for:
    - Basic cross-tabulations
    - Banner tables
    - Statistical significance testing
    - Effect size calculations
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the cross-tabulation engine.
        
        Args:
            data: DataFrame containing the data to analyze
        """
        self.data = data
        self._validate_data()
        self.generator = CrosstabGenerator(data)

    def _validate_data(self) -> None:
        """Validate the input data."""
        if self.data is None:
            raise ValueError("No data loaded")
        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")
        if self.data.empty:
            raise ValueError("DataFrame is empty")

    def create_crosstab(
        self,
        row_var: str,
        col_var: str,
        include_percentages: bool = True,
        include_statistics: bool = True
    ) -> CrosstabResult:
        """
        Create a cross-tabulation of two variables.

        Args:
            row_var (str): Name of the row variable
            col_var (str): Name of the column variable
            include_percentages (bool): Whether to include percentage calculations
            include_statistics (bool): Whether to include statistical tests

        Returns:
            CrosstabResult: The cross-tabulation result

        Raises:
            ValueError: If variables are not found in the data or if data is invalid
        """
        self._validate_data()

        if row_var not in self.data.columns:
            raise ValueError(f"Row variable '{row_var}' not found in data")
        if col_var not in self.data.columns:
            raise ValueError(f"Column variable '{col_var}' not found in data")

        # Check for all null values
        if self.data[row_var].isna().all() or self.data[col_var].isna().all():
            raise ValueError("Variable contains all null values")

        # Create frequency table
        table = pd.crosstab(
            self.data[row_var],
            self.data[col_var],
            margins=True,
            margins_name='All'
        )

        # Calculate percentages if requested
        row_percentages = None
        column_percentages = None
        total_percentages = None

        if include_percentages:
            # Convert table to float to avoid dtype warnings
            table = table.astype(float)

            # Row percentages (each row should sum to 100%)
            row_percentages = pd.DataFrame(index=table.index, columns=table.columns)
            for idx in table.index:
                if idx != 'All':
                    total = table.loc[idx, table.columns != 'All'].sum()
                    if total > 0:
                        row_percentages.loc[idx, table.columns != 'All'] = table.loc[idx, table.columns != 'All'] / total * 100
                        row_percentages.loc[idx, 'All'] = 100.0
                    else:
                        row_percentages.loc[idx, :] = 0.0
            # Calculate 'All' row percentages
            total = table.loc['All', table.columns != 'All'].sum()
            if total > 0:
                row_percentages.loc['All', table.columns != 'All'] = table.loc['All', table.columns != 'All'] / total * 100
                row_percentages.loc['All', 'All'] = 100.0
            else:
                row_percentages.loc['All', :] = 0.0

            # Column percentages (each column should sum to 100%)
            column_percentages = pd.DataFrame(index=table.index, columns=table.columns)
            for col in table.columns:
                if col != 'All':
                    total = table.loc[table.index != 'All', col].sum()
                    if total > 0:
                        column_percentages.loc[table.index != 'All', col] = table.loc[table.index != 'All', col] / total * 100
                        column_percentages.loc['All', col] = 100.0
                    else:
                        column_percentages.loc[:, col] = 0.0
            # Calculate 'All' column percentages
            total = table.loc[table.index != 'All', 'All'].sum()
            if total > 0:
                column_percentages.loc[table.index != 'All', 'All'] = table.loc[table.index != 'All', 'All'] / total * 100
                column_percentages.loc['All', 'All'] = 100.0
            else:
                column_percentages.loc[:, 'All'] = 0.0

            # Total percentages (all cells should sum to 100%, excluding margins)
            total = table.iloc[:-1, :-1].sum().sum()
            total_percentages = pd.DataFrame(index=table.index, columns=table.columns)
            if total > 0:
                total_percentages.iloc[:-1, :-1] = table.iloc[:-1, :-1] / total * 100
                total_percentages.iloc[-1, :-1] = table.iloc[-1, :-1] / total * 100
                total_percentages.iloc[:-1, -1] = table.iloc[:-1, -1] / total * 100
                total_percentages.iloc[-1, -1] = 100.0
            else:
                total_percentages.iloc[:, :] = 0.0
                total_percentages.iloc[-1, -1] = 100.0

        # Calculate statistics if requested
        statistics = None
        if include_statistics and not self.data.empty:
            # Remove margins for chi-square test
            chi2_table = table.iloc[:-1, :-1]
            
            # Handle single value case
            if chi2_table.shape[0] == 1 or chi2_table.shape[1] == 1:
                statistics = CrosstabStatistics(
                    chi_square=0.0,
                    p_value=1.0,
                    degrees_of_freedom=0.0,
                    cramers_v=0.0,
                    expected_values=chi2_table.values.tolist(),
                    residuals=[[0.0] * chi2_table.shape[1]] * chi2_table.shape[0]
                )
            else:
                chi2, p, dof, expected = stats.chi2_contingency(chi2_table)

                # Calculate Cramer's V
                n = chi2_table.sum().sum()
                min_dim = min(chi2_table.shape) - 1
                if n > 0 and min_dim > 0:
                    cramers_v = np.sqrt(chi2 / (n * min_dim))
                else:
                    cramers_v = 0.0

                # Create residuals matrix
                residuals = (chi2_table.values - expected) / np.sqrt(expected)

                statistics = CrosstabStatistics(
                    chi_square=float(chi2),
                    p_value=float(p),
                    degrees_of_freedom=float(dof),
                    cramers_v=float(cramers_v),
                    expected_values=expected.tolist(),
                    residuals=residuals.tolist()
                )

        return CrosstabResult(
            table=table,
            row_percentages=row_percentages,
            column_percentages=column_percentages,
            total_percentages=total_percentages,
            statistics=statistics
        )

    def create_banner_table(
        self,
        row_vars: List[str],
        col_vars: List[str],
        include_percentages: bool = True,
        include_statistics: bool = True
    ) -> Dict[str, CrosstabResult]:
        """
        Create a banner table with multiple variables.
        
        Args:
            row_vars: List of row variables
            col_vars: List of column variables
            include_percentages: Whether to include percentage calculations
            include_statistics: Whether to include statistical tests
            
        Returns:
            Dictionary of CrosstabResult objects for each combination
        """
        results = {}
        
        for row_var in row_vars:
            for col_var in col_vars:
                key = f"{row_var} x {col_var}"
                results[key] = self.create_crosstab(
                    row_var=row_var,
                    col_var=col_var,
                    include_percentages=include_percentages,
                    include_statistics=include_statistics
                )
                
        return results

    def _calculate_expected_values(self, table: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate expected values for a contingency table.
        
        Args:
            table: Contingency table
            
        Returns:
            DataFrame of expected values
        """
        row_totals = table.sum(axis=1)
        col_totals = table.sum(axis=0)
        total = table.sum().sum()
        
        expected = np.outer(row_totals, col_totals) / total
        return pd.DataFrame(expected, index=table.index, columns=table.columns)

    def _calculate_residuals(
        self,
        observed: pd.DataFrame,
        expected: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate standardized residuals.
        
        Args:
            observed: Observed values
            expected: Expected values
            
        Returns:
            DataFrame of standardized residuals
        """
        residuals = (observed - expected) / np.sqrt(expected)
        return residuals

    def _calculate_cramers_v(self, table: pd.DataFrame, chi2: float) -> float:
        """
        Calculate Cramer's V effect size.
        
        Args:
            table: Contingency table
            chi2: Chi-square statistic
            
        Returns:
            Cramer's V value
        """
        n = table.sum().sum()
        k = min(table.shape) - 1
        return np.sqrt(chi2 / (n * k))

    def perform_statistical_test(
        self,
        var1: str,
        var2: str,
        test_type: StatisticType
    ) -> StatisticalResult:
        """
        Perform a statistical test between two variables.
        
        Args:
            var1: First variable
            var2: Second variable
            test_type: Type of statistical test to perform
            
        Returns:
            StatisticalResult containing test results
        """
        if test_type == StatisticType.CHI_SQUARE:
            table = pd.crosstab(self.data[var1], self.data[var2])
            chi2, p, dof, _ = stats.chi2_contingency(table)
            return StatisticalResult(
                test_type=test_type,
                statistic=chi2,
                p_value=p,
                degrees_of_freedom=dof,
                effect_size=self._calculate_cramers_v(table, chi2)
            )
            
        elif test_type == StatisticType.FISHER_EXACT:
            table = pd.crosstab(self.data[var1], self.data[var2])
            odds_ratio, p = stats.fisher_exact(table)
            return StatisticalResult(
                test_type=test_type,
                statistic=odds_ratio,
                p_value=p
            )
            
        elif test_type == StatisticType.T_TEST:
            groups = self.data[var1].unique()
            if len(groups) != 2:
                raise ValueError("T-test requires exactly 2 groups")
                
            group1 = self.data[self.data[var1] == groups[0]][var2]
            group2 = self.data[self.data[var1] == groups[1]][var2]
            
            t_stat, p = stats.ttest_ind(group1, group2)
            effect_size = (group1.mean() - group2.mean()) / np.sqrt(
                (group1.var() + group2.var()) / 2
            )
            
            return StatisticalResult(
                test_type=test_type,
                statistic=t_stat,
                p_value=p,
                effect_size=effect_size
            )
            
        elif test_type == StatisticType.ANOVA:
            groups = self.data[var1].unique()
            if len(groups) < 2:
                raise ValueError("ANOVA requires at least 2 groups")
                
            group_data = [self.data[self.data[var1] == g][var2] for g in groups]
            f_stat, p = stats.f_oneway(*group_data)
            
            # Calculate eta squared
            total_ss = sum((x - self.data[var2].mean())**2 for x in self.data[var2])
            between_ss = sum(len(g) * (g.mean() - self.data[var2].mean())**2 for g in group_data)
            eta_squared = between_ss / total_ss
            
            return StatisticalResult(
                test_type=test_type,
                statistic=f_stat,
                p_value=p,
                degrees_of_freedom=(len(groups) - 1, len(self.data) - len(groups)),
                effect_size=eta_squared
            )
            
        else:
            raise ValueError(f"Unsupported test type: {test_type}") 