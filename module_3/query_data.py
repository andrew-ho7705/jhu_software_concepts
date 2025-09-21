import psycopg2


def connect_to_db():
    return psycopg2.connect(dbname="postgres", user="postgres")


def execute_query(description, query, multi_row=False):
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        if multi_row:
            results = cursor.fetchall()
            print(f"{description}")
            if results:
                for row in results:
                    print(f" {row}")
            else:
                print(" No data")
        else:
            result = cursor.fetchone()
            print(f"{description}\n {result[0] if result else 'No data'}")
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        cursor.close()
        conn.close()


def query_data():

    # How many entries do you have in your database who have applied for Fall 2025?
    query1 = """
    SELECT COUNT(*) 
    FROM applicants 
    WHERE term LIKE '%Fall 2025%'
    """
    execute_query("Fall 2025 Applicants", query1)

    # What percentage of entries are from international students (not American or Other) (to two decimal places)?
    query2 = """
    SELECT CAST(
        (COUNT(CASE WHEN us_or_international = 'International' THEN 1 END) * 100.0 / COUNT(*)) AS DECIMAL(4,2)
    )
    FROM applicants
    """
    execute_query("Percentage of international students", query2)

    # What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?
    query3a = """
    SELECT AVG(gpa) 
    FROM applicants 
    WHERE gpa IS NOT NULL
    """
    execute_query("Average GPA", query3a)

    query3b = """
    SELECT AVG(gre)  
    FROM applicants 
    WHERE gre IS NOT NULL
    """
    execute_query("Average GRE", query3b)

    query3c = """
    SELECT AVG(gre_v)
    FROM applicants 
    WHERE gre_v IS NOT NULL
    """
    execute_query("Average GRE V", query3c)

    query3d = """
    SELECT AVG(gre_aw) 
    FROM applicants 
    WHERE gre_aw IS NOT NULL
    """
    execute_query("Average GRE AW", query3d)

    # What is their average GPA of American students in Fall 2025?
    query4 = """
    SELECT AVG(gpa) 
    FROM applicants 
    WHERE us_or_international = 'American' 
    AND term LIKE '%Fall 2025%' 
    AND gpa IS NOT NULL
    """
    execute_query("Average GPA of American students in Fall 2025", query4)

    # What percent of entries for Fall 2025 are Acceptances (to two decimal places)?
    query5 = """
    SELECT CAST(
        (COUNT(CASE WHEN status LIKE '%Accepted%' THEN 1 END) * 100.0 / COUNT(*)) AS DECIMAL(5,2)
    )
    FROM applicants 
    WHERE term LIKE '%Fall 2025%'
    """
    execute_query("Percentage of Fall 2025 acceptances", query5)

    # What is the average GPA of applicants who applied for Fall 2025 who are Acceptances?
    query6 = """
    SELECT AVG(gpa) 
    FROM applicants 
    WHERE term LIKE '%Fall 2025%' 
    AND status LIKE '%Accepted%' 
    AND gpa IS NOT NULL
    """
    execute_query("Average GPA of Fall 2025 acceptances", query6)

    # How many entries are from applicants who applied to JHU for a masters degree in Computer Science?
    query7 = """
    SELECT COUNT(*) 
    FROM applicants 
    WHERE llm_generated_program LIKE '%Computer Science' 
    AND llm_generated_university LIKE '%Johns Hopkins%'
    """
    execute_query("JHU Computer Science applications", query7)

    # How many entries from 2025 are acceptances from applicants who applied to Georgetown University for a PhD in Computer Science?
    query8 = """
    SELECT COUNT(*) 
    FROM applicants 
    WHERE date_added >= '2025-01-01' 
    AND date_added < '2026-01-01' 
    AND status LIKE '%Accepted%' 
    AND llm_generated_program LIKE '%Computer Science' 
    AND llm_generated_university LIKE '%Georgetown%'
    """
    execute_query("2025 Georgetown CS acceptances", query8)
    
    # My Queries

    # What is the acceptance rate by degree level?
    query9 = """
    SELECT 
        degree,
        CAST(
            (COUNT(CASE WHEN status LIKE '%Accepted%' THEN 1 END) * 100.0 / COUNT(*)) AS float
        ) as acceptance_rate
    FROM applicants 
    WHERE degree IS NOT NULL
    GROUP BY degree 
    ORDER BY acceptance_rate ASC
    """
    execute_query("Acceptance rate by degree level", query9, multi_row=True)

    # Which universities have the lowest acceptance rate?
    query10 = """
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
    """
    execute_query(
        "Top 10 universities by acceptance rate",
        query10,
        multi_row=True,
    )


if __name__ == "__main__":
    query_data()
