Andrew Ho, 43BBA0

Module 2: Web Scraping

Approach:
I began by inspecting the structure of the HTML on both the /survey?page=... and the
/survey/result/... url paths. I found out that not all of the necessary information
in order to build each applicant object was available on their respective /survey/result/...
page, so I came up with a different approach. I realized that each survey page displayed the 
necessary added_on, decision, and term data that was not available on their respective page.
In the function scrape_survey_page, I scraped that data and stored each applicant entry in a 
dictionary with key id (from the href field from the "See more") button with values added_on,
decision, and term, then appended it to an array. After collecting ~30,000 ids, I passed this 
object along to scrape_raw_data. I looped through the survey object on its key id and 
destructured the value in order to grab the added_on, decision, and term data. From there, I 
used the key to scrape the rest of the data into another object that I constructed in order to
match the desired assignment output. With the raw scraped data, I passed it along to clean_data.
In clean_data, I combine the program and university field into just one field, set university
to empty quotes, and then remove any keys from the object if the value is falsy (except for 
comments). Finally, I have functions in order to save and load the json to/from a file.

Changes to app.py:
I added the following changes:
    to SYSTEM_PROMPT:
        - Never change the region/culture qualifier in program names (e.g., do not substitute 
        'Latin American' for 'Native American', 'East Asian' for 'South Asian', etc.).
    to FEW_SHOTS:
        (
            {"program": "Native American Studies, University of California, Davis"},
            {
                "standardized_program": "Native American Studies",
                "standardized_university": "University of California, Davis",
            },
        ),
        (
            {"program": "RonaldAnoms, Microsoft"},
            {
                "standardized_program": "RonaldAnoms",
                "standardized_university": "Microsoft",
            }
        ),
        (
            {"program": "Masters in Data Science and Artificial Intelligence, University of Waterloo"},
            {
                "standardized_program": "Data Science And Artificial Intelligence",
                "standardized_university": "University of Waterloo",
            },
        ),
        (
            {"program": "Institute of Health Policy, Management and Evaluation (Health System Research), University of Toronto"},
            {
                "standardized_program": "Health Policy, Management And Evaluation",
                "standardized_university": "University of Toronto",
            },
        )
I believe that these changes will improve the accuracy of the model since I provided more precise example.
There weren't any systematic edge cases that I encountered while I skimmed through the data.

Checked https://www.thegradcafe.com/robots.txt (under module_2/robots.text.png)