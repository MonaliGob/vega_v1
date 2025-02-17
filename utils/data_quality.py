# initial commit
import pandas as pd
from typing import Dict, List
import numpy as np
from sqlalchemy import text

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
