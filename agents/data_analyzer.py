import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import json
import asyncio
from datetime import datetime
import logging
from utils.llm_client import call_claude

logger = logging.getLogger(__name__)

class DataAnalyzerAgent:
    """Agent for data analysis and insights generation"""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'excel', 'parquet']
    
    async def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive analysis on a DataFrame"""
        
        analysis = {
            "shape": {
                "rows": len(df),
                "columns": len(df.columns)
            },
            "columns": {},
            "missing_values": {},
            "correlations": {},
            "summary_statistics": {},
            "data_quality": {
                "completeness": 0,
                "issues": []
            }
        }
        
        # Analyze each column
        for col in df.columns:
            col_analysis = {
                "dtype": str(df[col].dtype),
                "unique_values": int(df[col].nunique()),
                "missing_count": int(df[col].isna().sum()),
                "missing_percentage": float(df[col].isna().sum() / len(df) * 100)
            }
            
            # Additional analysis for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                col_analysis.update({
                    "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                    "median": float(df[col].median()) if not df[col].isna().all() else None,
                    "std": float(df[col].std()) if not df[col].isna().all() else None,
                    "min": float(df[col].min()) if not df[col].isna().all() else None,
                    "max": float(df[col].max()) if not df[col].isna().all() else None,
                    "quartiles": {
                        "25%": float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                        "50%": float(df[col].quantile(0.50)) if not df[col].isna().all() else None,
                        "75%": float(df[col].quantile(0.75)) if not df[col].isna().all() else None
                    }
                })
            
            # Additional analysis for categorical columns
            elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
                value_counts = df[col].value_counts().head(10)
                col_analysis["top_values"] = {
                    str(k): int(v) for k, v in value_counts.items()
                }
            
            # Additional analysis for datetime columns
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_analysis.update({
                    "min_date": str(df[col].min()) if not df[col].isna().all() else None,
                    "max_date": str(df[col].max()) if not df[col].isna().all() else None,
                    "date_range_days": int((df[col].max() - df[col].min()).days) if not df[col].isna().all() else None
                })
            
            analysis["columns"][col] = col_analysis
            analysis["missing_values"][col] = col_analysis["missing_percentage"]
        
        # Calculate correlations for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            # Find strong correlations (> 0.7 or < -0.7)
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:
                        strong_corr.append({
                            "col1": corr_matrix.columns[i],
                            "col2": corr_matrix.columns[j],
                            "correlation": float(corr_value)
                        })
            analysis["correlations"]["strong_correlations"] = strong_corr
        
        # Data quality metrics
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isna().sum().sum()
        analysis["data_quality"]["completeness"] = float((total_cells - missing_cells) / total_cells * 100)
        
        # Identify data quality issues
        issues = []
        for col in df.columns:
            if analysis["columns"][col]["missing_percentage"] > 50:
                issues.append(f"Column '{col}' has >50% missing values")
            
            if pd.api.types.is_numeric_dtype(df[col]):
                # Check for outliers using IQR method
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                if outliers > len(df) * 0.1:  # More than 10% outliers
                    issues.append(f"Column '{col}' has {outliers} potential outliers")
        
        analysis["data_quality"]["issues"] = issues
        
        # Summary statistics
        analysis["summary_statistics"] = json.loads(df.describe().to_json())
        
        return analysis
    
    async def detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect patterns and anomalies in the data"""
        
        patterns = []
        
        # Time series patterns
        date_cols = df.select_dtypes(include=['datetime64']).columns
        if len(date_cols) > 0:
            for date_col in date_cols:
                # Check for seasonality, trends, etc.
                df_sorted = df.sort_values(date_col)
                
                # Simple trend detection for numeric columns
                for num_col in df.select_dtypes(include=[np.number]).columns:
                    if df_sorted[num_col].notna().sum() > 10:
                        # Calculate correlation with time index
                        time_index = np.arange(len(df_sorted))
                        valid_mask = df_sorted[num_col].notna()
                        if valid_mask.sum() > 2:
                            corr = np.corrcoef(time_index[valid_mask], df_sorted[num_col][valid_mask])[0, 1]
                            if abs(corr) > 0.7:
                                patterns.append({
                                    "type": "temporal_trend",
                                    "column": num_col,
                                    "date_column": date_col,
                                    "correlation": float(corr),
                                    "direction": "increasing" if corr > 0 else "decreasing"
                                })
        
        # Duplicate detection
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            patterns.append({
                "type": "duplicates",
                "count": int(duplicates),
                "percentage": float(duplicates / len(df) * 100)
            })
        
        # Value distribution patterns
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].notna().sum() > 10:
                # Check for normal distribution
                from scipy import stats
                _, p_value = stats.normaltest(df[col].dropna())
                if p_value > 0.05:
                    patterns.append({
                        "type": "distribution",
                        "column": col,
                        "distribution": "normal",
                        "p_value": float(p_value)
                    })
                
                # Check for bimodal distribution
                hist, bins = np.histogram(df[col].dropna(), bins=20)
                peaks = []
                for i in range(1, len(hist)-1):
                    if hist[i] > hist[i-1] and hist[i] > hist[i+1]:
                        peaks.append(i)
                if len(peaks) >= 2:
                    patterns.append({
                        "type": "distribution",
                        "column": col,
                        "distribution": "multimodal",
                        "peaks": len(peaks)
                    })
        
        return patterns
    
    async def generate_insights(self, analysis: Dict[str, Any], patterns: List[Dict[str, Any]]) -> str:
        """Generate natural language insights using Claude"""
        
        prompt = f"""Based on the following data analysis results, provide key insights and recommendations:

Data Overview:
- Shape: {analysis['shape']['rows']} rows × {analysis['shape']['columns']} columns
- Data Quality: {analysis['data_quality']['completeness']:.1f}% complete

Column Analysis:
{json.dumps(analysis['columns'], indent=2)}

Detected Patterns:
{json.dumps(patterns, indent=2)}

Data Quality Issues:
{json.dumps(analysis['data_quality']['issues'], indent=2)}

Please provide:
1. 3-5 key insights about the data
2. Potential concerns or data quality issues
3. Recommendations for further analysis or data cleaning
4. Any interesting patterns or relationships discovered

Format as a clear, concise report suitable for stakeholders."""
        
        insights = await call_claude(prompt)
        return insights
    
    async def perform_statistical_tests(self, df: pd.DataFrame, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform various statistical tests based on configuration"""
        
        from scipy import stats
        results = {}
        
        # T-test for comparing means
        if "t_test" in test_config:
            config = test_config["t_test"]
            group_col = config.get("group_column")
            value_col = config.get("value_column")
            
            if group_col and value_col and group_col in df.columns and value_col in df.columns:
                groups = df[group_col].unique()
                if len(groups) == 2:
                    group1 = df[df[group_col] == groups[0]][value_col].dropna()
                    group2 = df[df[group_col] == groups[1]][value_col].dropna()
                    
                    t_stat, p_value = stats.ttest_ind(group1, group2)
                    results["t_test"] = {
                        "groups": list(groups),
                        "t_statistic": float(t_stat),
                        "p_value": float(p_value),
                        "significant": p_value < 0.05
                    }
        
        # Chi-square test for independence
        if "chi_square" in test_config:
            config = test_config["chi_square"]
            col1 = config.get("column1")
            col2 = config.get("column2")
            
            if col1 and col2 and col1 in df.columns and col2 in df.columns:
                contingency_table = pd.crosstab(df[col1], df[col2])
                chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
                
                results["chi_square"] = {
                    "columns": [col1, col2],
                    "chi2_statistic": float(chi2),
                    "p_value": float(p_value),
                    "degrees_of_freedom": int(dof),
                    "significant": p_value < 0.05
                }
        
        # ANOVA for comparing multiple groups
        if "anova" in test_config:
            config = test_config["anova"]
            group_col = config.get("group_column")
            value_col = config.get("value_column")
            
            if group_col and value_col and group_col in df.columns and value_col in df.columns:
                groups = []
                for name, group in df.groupby(group_col):
                    groups.append(group[value_col].dropna())
                
                if len(groups) > 2:
                    f_stat, p_value = stats.f_oneway(*groups)
                    results["anova"] = {
                        "f_statistic": float(f_stat),
                        "p_value": float(p_value),
                        "significant": p_value < 0.05,
                        "num_groups": len(groups)
                    }
        
        return results

async def run_data_analyzer_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for the data analyzer agent"""
    
    data = params.get("data", None)
    file_path = params.get("file_path", None)
    analysis_type = params.get("analysis_type", "comprehensive")
    statistical_tests = params.get("statistical_tests", None)
    
    analyzer = DataAnalyzerAgent()
    
    try:
        # Load data into DataFrame
        if file_path:
            # Load from file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            else:
                return {
                    "status": "error",
                    "error": f"Unsupported file format: {file_path}"
                }
        elif data:
            # Load from provided data
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return {
                    "status": "error",
                    "error": "Invalid data format"
                }
        else:
            return {
                "status": "error",
                "error": "No data or file path provided"
            }
        
        # Perform analysis based on type
        results = {
            "status": "completed",
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }
        
        if analysis_type in ["comprehensive", "basic"]:
            # Basic data analysis
            analysis = await analyzer.analyze_dataframe(df)
            results["analysis"] = analysis
            
            if analysis_type == "comprehensive":
                # Pattern detection
                patterns = await analyzer.detect_patterns(df)
                results["patterns"] = patterns
                
                # Generate insights
                insights = await analyzer.generate_insights(analysis, patterns)
                results["insights"] = insights
        
        # Perform statistical tests if requested
        if statistical_tests:
            test_results = await analyzer.perform_statistical_tests(df, statistical_tests)
            results["statistical_tests"] = test_results
        
        return results
        
    except Exception as e:
        logger.error(f"Data analyzer agent failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }