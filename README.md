# una_health_challenge

 Demonstration of celery and redis as a message broker 

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Assumptions](#assumptions)
- [Detailed Description](#detailed_description)
  
## Installation

1. Clone the repository:

    ```bash
    gh repo clone dipikasgp/una_health_challenge
    ```

2. Navigate to the project directory:

    ```bash
    cd una_health_challenge
    ```



3. Set up environment variables (if any).

## Usage

1. Start the Flask server:

    ```bash
    python run.py
    ```

## Assumptions:
1. Considered user_id, device, serial_number, device_timestamp,	recording_type,	glucose_level columns are considered and added in the database.
2. Translated the column names to english for ease of use
3. Removed the columns where glucose level is not present.
   



## Detailed Description
There are total 4 APIs in the solution. There is only one table glucose_tracker which contains user_id, device, serial_number, device_timestamp,	recording_type,	glucose_level.
The populate_database API populates the database with the data from the excel files and the GET APIs use this data to return the filtered data.

1. [GET]/api/v1/levels/ - Retrives the glucose levels which matches the user_id. It returns a paginated sorted list of glucose level.
2. [GET]/api/v1/levels/<id>/ - Retrieves the glucose levels by passing the  id(user_id) through path param
3. [POST]/api/v1/populate_db/ - Fetches the excel files from the data_file folder and preprocesses it to remove the first 2 rows. Renames the column names to english and removes the nan values from glucose level column assuming no tracking should be done for the data which is not present. Then it bulk inserts the dataframe to the glucose_track table. It throws an error in case of error else returns a success message.
5. [POST]/api/v1/export_to_excel/ - Fetches all the data from the db table and dumps it into excel.

   


