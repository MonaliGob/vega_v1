import pandas as pd
from typing import Dict, List
import numpy as np
from sqlalchemy import text
import re
from datetime import datetime
from scipy import stats

class DataQualityChecker:
    @staticmethod
    def generate_completeness_query(table: str, column: str) -> str:
        return f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT({column}) as non_null_rows,
            (COUNT({column})::float / COUNT(*)::float * 100) as completeness_score
        FROM {table}
        """

    @staticmethod
    def generate_uniqueness_query(table: str, column: str) -> str:
        return f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT {column}) as unique_values,
            (COUNT(DISTINCT {column})::float / COUNT(*)::float * 100) as uniqueness_score
        FROM {table}
        """

    @staticmethod
    def generate_range_query(table: str, column: str, min_val: float, max_val: float) -> str:
        return f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(CASE WHEN {column}::numeric >= {min_val} AND {column}::numeric <= {max_val} THEN 1 END) as valid_rows,
            (COUNT(CASE WHEN {column}::numeric >= {min_val} AND {column}::numeric <= {max_val} THEN 1 END)::float / COUNT(*)::float * 100) as range_score
        FROM {table}
        WHERE {column} IS NOT NULL
        """

    @staticmethod
    def generate_pattern_query(table: str, column: str, pattern: str) -> str:
        return f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(CASE WHEN {column} ~ '{pattern}' THEN 1 END) as valid_rows,
            (COUNT(CASE WHEN {column} ~ '{pattern}' THEN 1 END)::float / COUNT(*)::float * 100) as pattern_score
        FROM {table}
        WHERE {column} IS NOT NULL
        """

    @staticmethod
    def generate_date_format_query(table: str, column: str, format: str = 'YYYY-MM-DD') -> str:
        return f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(CASE WHEN TO_CHAR({column}::timestamp, '{format}') IS NOT NULL THEN 1 END) as valid_rows,
            (COUNT(CASE WHEN TO_CHAR({column}::timestamp, '{format}') IS NOT NULL THEN 1 END)::float / COUNT(*)::float * 100) as date_format_score
        FROM {table}
        WHERE {column} IS NOT NULL
        """

    @staticmethod
    def generate_cross_column_query(table: str, column1: str, column2: str, operator: str, value: str = None) -> str:
        condition = f"{column1} {operator} {column2}"
        if value:
            condition = f"{column1} {operator} {value}"

        return f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(CASE WHEN {condition} THEN 1 END) as valid_rows,
            (COUNT(CASE WHEN {condition} THEN 1 END)::float / COUNT(*)::float * 100) as cross_column_score
        FROM {table}
        WHERE {column1} IS NOT NULL AND {column2} IS NOT NULL
        """

    @staticmethod
    def generate_statistical_query(table: str, column: str, method: str = 'zscore', threshold: float = 3.0) -> str:
        return f"""
        WITH stats AS (
            SELECT 
                AVG({column}::numeric) as mean,
                STDDEV({column}::numeric) as stddev
            FROM {table}
            WHERE {column} IS NOT NULL
        ),
        z_scores AS (
            SELECT 
                {column}::numeric,
                (({column}::numeric - stats.mean) / stats.stddev) as zscore
            FROM {table}, stats
            WHERE {column} IS NOT NULL
        )
        SELECT 
            COUNT(*) as total_rows,
            COUNT(CASE WHEN ABS(zscore) <= {threshold} THEN 1 END) as valid_rows,
            (COUNT(CASE WHEN ABS(zscore) <= {threshold} THEN 1 END)::float / COUNT(*)::float * 100) as statistical_score
        FROM z_scores
        """

    @staticmethod
    def execute_rule(engine, rule: Dict) -> Dict:
        result = {
            'rule_id': rule['id'],
            'rule_name': rule['name'],
            'status': 'Success',
            'score': 0.0,
            'error': None,
            'query': ''
        }

        try:
            if rule['type'] == 'completeness':
                query = DataQualityChecker.generate_completeness_query(rule['table'], rule['column'])
                score_index = 2
            elif rule['type'] == 'uniqueness':
                query = DataQualityChecker.generate_uniqueness_query(rule['table'], rule['column'])
                score_index = 2
            elif rule['type'] == 'range':
                params = rule.get('parameters', {})
                min_val = float(params.get('min_val', 0))
                max_val = float(params.get('max_val', 100))
                query = DataQualityChecker.generate_range_query(rule['table'], rule['column'], min_val, max_val)
                score_index = 2
            elif rule['type'] == 'pattern':
                params = rule.get('parameters', {})
                pattern = params.get('pattern', '')
                query = DataQualityChecker.generate_pattern_query(rule['table'], rule['column'], pattern)
                score_index = 2
            elif rule['type'] == 'date_format':
                params = rule.get('parameters', {})
                format = params.get('format', 'YYYY-MM-DD')
                query = DataQualityChecker.generate_date_format_query(rule['table'], rule['column'], format)
                score_index = 2
            elif rule['type'] == 'cross_column':
                params = rule.get('parameters', {})
                column2 = params.get('column2', '')
                operator = params.get('operator', '=')
                value = params.get('value', None)
                query = DataQualityChecker.generate_cross_column_query(rule['table'], rule['column'], column2, operator, value)
                score_index = 2
            elif rule['type'] == 'statistical':
                params = rule.get('parameters', {})
                method = params.get('method', 'zscore')
                threshold = float(params.get('threshold', 3.0))
                query = DataQualityChecker.generate_statistical_query(rule['table'], rule['column'], method, threshold)
                score_index = 2
            else:
                raise ValueError(f"Unsupported rule type: {rule['type']}")

            result['query'] = query

            with engine.connect() as connection:
                result_set = connection.execute(text(query)).fetchone()
                if result_set is not None:
                    result['score'] = float(result_set[score_index])
                else:
                    raise ValueError("No results returned from query")

        except Exception as e:
            result['status'] = 'Failed'
            result['error'] = str(e)

        return result