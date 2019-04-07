# multi_class_text_classification
A way to classify the data into different classes

This is an event classification code in Python which can be integrated with Scrapy while scraping data from other sites. 
I have 30+ categories right now. 
Now categories are of two types:

a) All time - this type of categories are always live on our site 

b) Seasoned - this type of categories are active for sometime and then we make them inactive. For ex., New year event, Holi event.

Seasoned categories are country specific because Holi events happen only in India. Like this every country has their own festivals.

Every category has multiple sub-categories, ex., Festivals category has Holi, Diwali etc., so events should be classified into these sub-categories as well.

Few events are written in regional languages like Hindi, Urdu etc., we need to look into this also.

There is file with the name text_class.py the task of the code present in the file is that to classify the different text into different categories initially when we run this file it will first display the different categories present inside the dataset on which it is being trained and further when we pass the test dataset the model classifiy the dataset as per categories on which it is being trained.

To run the file type the command:
```
foo@bar$ python text_class.py
```

The above command will be trained on the given dataset and there is *pymysql library* that is being used for connecting to the server for fetching the data and classifying the data as per need since this should be used for text classification.
