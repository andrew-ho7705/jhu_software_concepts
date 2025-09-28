"""
Database query module for TheGradCafe data analysis.
"""

import os
import psycopg
from psycopg import sql

table_ident = sql.Identifier("applicants")

def connect_to_db():
    """
    Connect to PostgreSQL database.

    Returns:
        psycopg2.connection: Database connection object.
    """

    return psycopg.connect(os.environ.get("DATABASE_URL"))


def execute_query(query, multi_row=False):
    """
    Execute SQL query and return results.

    Args:
        query: SQL query to execute.
        multi_row: If True, fetch all rows; otherwise fetch one value.

    Returns:
        Query result: single value or list of rows.
    """

    with connect_to_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            if multi_row:
                results = cursor.fetchall()
            else:
                result = cursor.fetchone()
                results = result[0] if result else None
    return results

# def query_data(execute_query_cb, table="applicants"):
def query_data(execute_query_cb):
    """
    Run predefined analysis queries on the applicants table.

    Args:
        execute_query: Function to execute SQL queries.

    Returns:
        dict: Results of all queries (q1-q10).
    """

    # Query 1
    q1 = execute_query_cb(
        sql.SQL("""
            SELECT COUNT(*) FROM {table} WHERE term LIKE {term}
        """).format(
            table=table_ident,
            term=sql.Literal('%Fall 2025%')
        )
    )

    # Query 2
    q2 = execute_query_cb(
        sql.SQL("""
            SELECT CAST(
                (COUNT(CASE WHEN us_or_international = 'International' THEN 1 END) * 100.0 / COUNT(*)) 
                AS DECIMAL(4,2)
            )
            FROM {table}
        """).format(
        table=table_ident
        )
    )

    # Query 3a–3d
    q3a = execute_query_cb(
        sql.SQL("""
            SELECT AVG(gpa) FROM {table} WHERE gpa IS NOT NULL"""
        ).format(
            table=table_ident
        )
    )
    q3b = execute_query_cb(
        sql.SQL("""
            SELECT AVG(gre) FROM {table} WHERE gre IS NOT NULL"""
        ).format(
            table=table_ident
        )
    )
    q3c = execute_query_cb(
        sql.SQL("""
            SELECT AVG(gre_v) FROM {table} WHERE gre_v IS NOT NULL"""
        ).format(
            table=table_ident
        )
    )
    q3d = execute_query_cb(
        sql.SQL("""
            SELECT AVG(gre_aw) FROM {table} WHERE gre_aw IS NOT NULL"""
        ).format(
            table=table_ident
        )
    )

    # Query 4
    q4 = execute_query_cb(
        sql.SQL("""
            SELECT AVG(gpa) 
            FROM {table} 
            WHERE us_or_international = {us} AND term LIKE {term} AND gpa IS NOT NULL
        """).format(
            table=table_ident,
            us=sql.Literal('American'),
            term=sql.Literal('%Fall 2025%')
        )
    )

    # Query 5
    q5 = execute_query_cb(
        sql.SQL("""
            SELECT CAST(
                (COUNT(CASE WHEN status LIKE {status} THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0)) 
                AS DECIMAL(5,2)
            )
            FROM {table}
            WHERE term LIKE {term}
        """).format(
            table=table_ident,
            status=sql.Literal('%Accepted%'),
            term=sql.Literal('%Fall 2025%')
        )
    )

    # Query 6
    q6 = execute_query_cb(
        sql.SQL("""
            SELECT AVG(gpa) 
            FROM {table} 
            WHERE term LIKE {term} AND status LIKE {status} AND gpa IS NOT NULL
        """).format(
            table=table_ident,
            term=sql.Literal('%Fall 2025%'),
            status=sql.Literal('%Accepted%')
        )
    )

    # Query 7
    q7 = execute_query_cb(
        sql.SQL("""
            SELECT COUNT(*) 
            FROM {table} 
            WHERE llm_generated_program LIKE {program} 
            AND llm_generated_university LIKE {univ}
        """).format(
            table=table_ident,
            program=sql.Literal('%Computer Science'),
            univ=sql.Literal('%Johns Hopkins%')
        )
    )

    # Query 8
    q8 = execute_query_cb(
        sql.SQL("""
            SELECT COUNT(*) 
            FROM {table} 
            WHERE date_added >= {start} 
            AND date_added < {end} 
            AND status LIKE {status} 
            AND llm_generated_program LIKE {program} 
            AND llm_generated_university LIKE {univ}
        """).format(
            table=table_ident,
            start=sql.Literal('2025-01-01'),
            end=sql.Literal('2026-01-01'),
            status=sql.Literal('%Accepted%'),
            program=sql.Literal('%Computer Science'),
            univ=sql.Literal('%Georgetown%')
        )
    )

    # Query 9
    q9 = execute_query_cb(
        sql.SQL("""
            SELECT degree,
                CAST((COUNT(CASE WHEN status LIKE {status} THEN 1 END) * 100.0 / COUNT(*)) AS double precision) AS acceptance_rate
            FROM {table}
            WHERE degree IS NOT NULL
            GROUP BY degree
            ORDER BY acceptance_rate ASC
        """).format(
            table=table_ident,
            status=sql.Literal('%Accepted%')
        ),
        multi_row=True
    )

    # Query 10
    q10 = execute_query_cb(
        sql.SQL("""
            SELECT llm_generated_university,
                CAST((COUNT(CASE WHEN status LIKE {status} THEN 1 END) * 100.0 / COUNT(*)) AS float) AS acceptance_rate
            FROM {table}
            WHERE llm_generated_university IS NOT NULL
            GROUP BY llm_generated_university
            HAVING COUNT(*) >= 25
            ORDER BY acceptance_rate ASC
            LIMIT 10
        """).format(
            table=table_ident,
            status=sql.Literal('%Accepted%')
        ),
        multi_row=True
    )

    return {
        "q1": q1,
        "q2": q2,
        "q3a": q3a,
        "q3b": q3b,
        "q3c": q3c,
        "q3d": q3d,
        "q4": q4,
        "q5": q5,
        "q6": q6,
        "q7": q7,
        "q8": q8,
        "q9": q9,
        "q10": q10,
    }
