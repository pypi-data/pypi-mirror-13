Sooty: Simple Database Migrator
========================

Sooty is a simple database migration tool for postgres databases. When working with a legacy application, more often than not, the application has no means of migrating the database forward. This is a simple library to bridge that gap.

The name Sooty comes from the bird Sooty Shearwater which can travel over 20,000 miles during it's annual migration. https://en.wikipedia.org/wiki/Sooty_shearwater

Usage
------------

.. code:: sh

    sooty create add index on product ids

    $ Created directory './migrations'
    $ Created migration file './migrations/create_index_on_product_ids_20160218223012.sql

    $ cat ./migrations/create_index_on_product_ids_20160218223012.sql
    
    -- Just type some SQL!
    -- ALTER TABLE products ADD COLUMN customer_code varchar(11)
    


To run your migrations just


.. code:: sh

    $ sooty run <database_url>


If no database url is provided, sooty will try to use the environment variable DATABASE_URL



That's it!
