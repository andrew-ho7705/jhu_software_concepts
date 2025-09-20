import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from module_2.clean import load_data

conn = psycopg2.connect(dbname="postgres", user="postgres")
llm_extend_applicant_data = load_data("../module_2/llm_extend_applicant_data.json")

print(llm_extend_applicant_data[0])
# with conn.cursor() as cur:
    
