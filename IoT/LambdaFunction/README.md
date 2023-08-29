# Setting Up and Running Lambda Function to Write Data to AWS RDS

## This README file provides instructions on setting up and running a Lambda function that receives messages from AWS IoT Core and writes them to an RDS database. You will need to prepare configuration data beforehand and follow the steps outlined below.

## Folder Contents

* `config.py`: File containing configuration data such as AWS RDS endpoint, master username, master password, and database name.
* `lambda_function.py`: Lambda function code that processes messages from AWS IoT Core and writes them to the RDS database.
* `requirements.txt`: List of Python dependencies for the Lambda function.
* `install.sh`: Script to create a zip file containing the function code and dependencies ready for uploading to AWS Lambda.


## Setup and Execution Steps
1. **Configure the Configuration Data**

    In the `config.py` file, specify the following configuration data:
    
    ```python
    # config.py
    
    host = "your_rds_endpoint"
    user = "your_master_username"
    password = "your_master_password"
    db_name = "your_database_name"
    ```

2. **Create and Package the Lambda Function**

    Run the `install.sh` script to create a zip file ready for upload to AWS Lambda:
    
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    This command will create a file named `lambda_function.zip` in the folder with your files.
