Description: Create a single dummy user in the database
Allowed-tools: Read, Bash(py:*)

Read database/db.py to understand the users table schema and the get_db() helper.

Then write and run a Python script using Bash that:

1. Generates a realistic random Indian user using your own knowledge of common Indian names across regions:
   - Name: a realistic Indian first + last name
   - Email: derived from the name with a random 2-3 digit number suffix
     (e.g. rahul.sharma91@gmail.com)
   - Password: "password123" hashed with werkzeug's generate_password_hash
   - created_at: current datetime
2. Checks if the generated email already exists in the users table.
3. If the email already exists, generate a different user and try again until a unique email is found.
4. Inserts the user into the users table using the existing database connection pattern from get_db().
5. Prints the inserted user's details:
   - id
   - name
   - email
   - created_at
6. Verifies the record was inserted successfully by querying it back from the database.
Do not modify any application source code files. Create and execute a standalone script only. Remove the script after successful execution.
