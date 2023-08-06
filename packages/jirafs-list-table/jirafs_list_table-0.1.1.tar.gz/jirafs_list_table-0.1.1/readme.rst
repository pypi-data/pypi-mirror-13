Jirafs list-table Macro
=======================

Adds a macro used for transforming a list into a table, for example::

  {list-table}
  *
  ** Capital
  ** Population (millions)
  * Canada
  ** Ottawa, Ontario
  ** 35.16
  * United States of America
  ** Washington, DC
  ** 318.9
  * Mexico
  ** Mexico City, DF
  ** 122.3
  * Guatemala
  ** Guatemala City
  ** 15.47
  {list-table}

will be automatically transformed into JIRA's special markup::

  || ||Canada||United States of America||Mexico||Guatemala||
  |Capital|Ottawa, Ontario|Washington, DC|Mexico City, DF|Guatemala City|
  |Population (millions)|35.16|318.9|122.3|15.47|

which, when rendered by JIRA, will look something like this:

+------------+-----------------+--------------------------+-----------------+----------------+
|            | Canada          | United States of America | Mexico          | Guatemala      |
+============+=================+==========================+=================+================+
| Capital    | Ottawa, Ontario | Washington, DC           | Mexico City, DF | Guatemala City |
+------------+-----------------+--------------------------+-----------------+----------------+
| Population | 35.16           | 318.9                    | 122.3           | 15.47          |
| (millions) |                 |                          |                 |                |
+------------+-----------------+--------------------------+-----------------+----------------+


Installation
------------

1. Install from PIP::

    pip install jirafs_list_table

2. Enable for a ticket folder::

    jirafs plugins --enable=list_table

Note that you can globally enable this (or any) plugin by adding the
``--global`` flag to the above command::

    jirafs plugins --global --enable=list_table

