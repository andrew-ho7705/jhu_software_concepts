import psycopg2


def connect_to_db():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        host="localhost",
        port=5432
    )


def execute_query(query, multi_row=False):
    conn = connect_to_db()
    cursor = conn.cursor()
    results = None
    cursor.execute(query)
    if multi_row:
        results = cursor.fetchall()
    else:
        result = cursor.fetchone()
        results = result[0] if result else None
    cursor.close()
    conn.close()
    return results


def query_data(execute_query):
    # Query 1
    q1 = execute_query(
        """
        SELECT COUNT(*) 
        FROM applicants 
        WHERE term LIKE '%Fall 2025%'
        """)

    # Query 2
    q2 = execute_query( 
        """
        SELECT CAST(
            (COUNT(CASE WHEN us_or_international = 'International' THEN 1 END) * 100.0 / COUNT(*)) AS DECIMAL(4,2)
        )
        FROM applicants
        """)

    # Query 3a–3d
    q3a = execute_query(
        "SELECT AVG(gpa) FROM applicants WHERE gpa IS NOT NULL")
    q3b = execute_query(
        "SELECT AVG(gre) FROM applicants WHERE gre IS NOT NULL")
    q3c = execute_query(
        "SELECT AVG(gre_v) FROM applicants WHERE gre_v IS NOT NULL")
    q3d = execute_query(
        "SELECT AVG(gre_aw) FROM applicants WHERE gre_aw IS NOT NULL")

    # Query 4
    q4 = execute_query(
        """
        SELECT AVG(gpa) 
        FROM applicants 
        WHERE us_or_international = 'American' 
        AND term LIKE '%Fall 2025%' 
        AND gpa IS NOT NULL
        """)

    # Query 5
    q5 = execute_query(
        """
        SELECT CAST(
            (COUNT(CASE WHEN status LIKE '%Accepted%' THEN 1 END) * 100.0 / COUNT(*)) AS DECIMAL(5,2)
        )
        FROM applicants 
        WHERE term LIKE '%Fall 2025%'
        """)

    # Query 6
    q6 = execute_query(
        """
        SELECT AVG(gpa) 
        FROM applicants 
        WHERE term LIKE '%Fall 2025%' 
        AND status LIKE '%Accepted%' 
        AND gpa IS NOT NULL
        """)

    # Query 7
    q7 = execute_query(
        """
        SELECT COUNT(*) 
        FROM applicants 
        WHERE llm_generated_program LIKE '%Computer Science' 
        AND llm_generated_university LIKE '%Johns Hopkins%'
        """)

    # Query 8
    q8 = execute_query(
        """
        SELECT COUNT(*) 
        FROM applicants 
        WHERE date_added >= '2025-01-01' 
        AND date_added < '2026-01-01' 
        AND status LIKE '%Accepted%' 
        AND llm_generated_program LIKE '%Computer Science' 
        AND llm_generated_university LIKE '%Georgetown%'
        """)

    # Query 9
    q9 = execute_query(
        """
        SELECT 
            degree,
            CAST(
                (COUNT(CASE WHEN status LIKE '%Accepted%' THEN 1 END) * 100.0 / COUNT(*)) AS double precision
            ) as acceptance_rate
        FROM applicants 
        WHERE degree IS NOT NULL
        GROUP BY degree 
        ORDER BY acceptance_rate ASC
        """, 
        multi_row=True)

    # Query 10
    q10 = execute_query(
        """
        SELECT 
            llm_generated_university,
            CAST(
                (COUNT(CASE WHEN status LIKE '%Accepted%' THEN 1 END) * 100.0 / COUNT(*)) AS float
            ) as acceptance_rate
        FROM applicants 
        WHERE llm_generated_university IS NOT NULL 
        GROUP BY llm_generated_university 
        HAVING COUNT(*) >= 25
        ORDER BY acceptance_rate ASC
        LIMIT 10
        """, 
        multi_row=True)

    return {
        "q1": q1,
        "q2": q2,
        "q3a": q3a, "q3b": q3b, "q3c": q3c, "q3d": q3d,
        "q4": q4,
        "q5": q5,
        "q6": q6,
        "q7": q7,
        "q8": q8,
        "q9": q9,
        "q10": q10
    }
