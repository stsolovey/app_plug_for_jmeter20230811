
### Legend and Theme:
We emulated a system (perhaps a mobile operator?) for load testing, with features such as registration, login, plan selection, and file operations.

### Emulator's methods:

1. **Authorization**:
    - **Endpoint**: `/register` (POST)
    - **Description**: Registers a new user to the system by accepting a JSON object with user details such as name, email, phone number, and password.
    
    - **Endpoint**: `/login` (POST)
    - **Description**: Allows a user to log in by providing their email and password. The method returns a JWT token if the login is successful.
  
2. **XML Requests**:
    - **Endpoint**: `/plan_selection` (POST)
    - **Description**: Accepts XML in the body of the request for selecting a plan for the user. This route is protected by JWT, ensuring only authenticated users can access it.
    
    - **Endpoint**: `/update_email` (POST)
    - **Description**: Accepts XML in the body of the request to update the email of the authenticated user.
    
    - **Endpoint**: `/update_password` (POST)
    - **Description**: Accepts XML in the body of the request to update the password of the authenticated user. This method also demonstrates the RSA encryption of the XML request header, as described in Task 2.3.
  
3. **Database Interactions**:
    - **Endpoint**: `/get_random_mobile_traffic` (GET)
    - **Description**: Queries the database to fetch a random set of 200 rows of mobile traffic data. This fulfills the task of retrieving large amounts of data from the database.
  
4. **File Operations**:
    - **Endpoint**: `/download_call_records/<file_size>` (GET)
    - **Description**: Allows authenticated users to download call record files of a specified size.
    
    - **Endpoint**: `/upload` (POST)
    - **Description**: Accepts files from users and saves them to the server. This method demonstrates the uploading functionality for large files.

## File Setup for Load Testing

To use this application with JMeter for load testing, you'll need to add specific files to the `files/download` directory. The files you add will depend on the desired load you want to test. Here are the recommended files:

- `5MB.zip`: For light load testing.
- `10MB.zip`: For moderate load.
- `20MB.zip`: Provides a heavier load.
- `100MB.zip`: For more intensive load testing scenarios.
- `200MB.zip`: Use with caution, as it will significantly increase the load.
- `512MB.zip`: For very high load testing scenarios.
- `1GB.zip`: Only recommended for stress testing to the maximum capacity.

Choose and add the appropriate files based on your testing requirements.

## Database Setup

This application relies on a PostgreSQL database. Ensure you have PostgreSQL installed and properly configured before running the application.

### Database Connection
To connect to the database, utilize the .env configuration file. Below is a template to guide your setup. Please adjust the values according to your environment and specific requirements.

```
FLASK_ENV=dev
DEVELOPMENT_DATABASE_URI=postgresql://postgres:123456@localhost/beeline_plug
PRODUCTION_DATABASE_URI=postgresql://your_production_db_uri_here
JWT_SECRET_KEY=a-very-secret-key
HOST=0.0.0.0
DEBUG=False
PORT=5000
```

Ensure the .env file is located at the root of your project directory and is added to your .gitignore to prevent sensitive data from being exposed.

### Automatic Table Creation

Upon initial setup, the table for users will be created automatically.

### Manual Table Creation: Mobile Traffic

However, you will need to create the `mobile_traffic` table manually. Here's the table structure using SQLAlchemy:

```python
from sqlalchemy import create_engine, Column, Integer, BigInteger, Text, Date, Time, String, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MobileTraffic(Base):
    __tablename__ = 'mobile_traffic'
    
    id_0 = Column(BigInteger, primary_key=True)
    id_a = Column(BigInteger)
    id_b = Column(BigInteger)
    start_time_local = Column(Time)
    time_zone = Column(Integer)
    duration = Column(Integer)
    forward = Column(Integer)
    zero_call_flg = Column(Integer)
    source_b = Column(Integer)
    source_f = Column(Integer)
    num_b_length = Column(Integer)
    time_key = Column(Date)

Base.metadata.create_all(engine)
```

### Data Population

Data for the `mobile_traffic` table can either be generated or fetched from external datasets. A recommended dataset can be found on Kaggle: [BestHack2022Beeline project](https://www.kaggle.com/datasets/sweetpunk/besthack2022beeline).

Particularly, you can use files like [time_key2021-11-03.csv](https://www.kaggle.com/datasets/sweetpunk/besthack2022beeline?select=time_key2021-11-03.csv) to populate the table.

To add the data to the database, you can use the following approach:

```python
import pandas as pd

dataframe = pd.read_csv('time_key2021-11-21.csv')
dataframe.to_sql('mobile_traffic', engine, if_exists='append', index=False, method='multi', chunksize=10000)
```

