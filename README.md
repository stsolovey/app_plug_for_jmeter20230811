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

