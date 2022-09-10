# Introduction

This client was created to interface with Notion using the official API and Python.

# Important Notes


1. **All databases you plan to use, including any relations of rollups, must be added to the integration.**

2. **Items in the `Title` column should all have unique names. Duplicates will create errors with this client.**

3. **Items in the `Title` column should not be empty.**

# Setup

A Notion integration must be made before using this client. Click [here](https://developers.notion.com/docs/getting-started) for more information. 
Follow Steps 1 & 2. Ensure all content capabilities are enabled.

Next, copy the `Notion.py` and `notion_key.py` to the directory your script is using.
Change the `key` variable found in `notion_key.py` to the token obtained from the Notion integration.

This client can then be used by importing the `Notion` class and creating an object from it as follows:

```python
import Notion

# Initialize Database ID
database_id = '087ed092c10f4535a91b7849b6f61928'
# Initialize Notion object 
N = Notion(database_id)
```

# Reading Data

Data can be read from the desired database using the following methods. 
These are written in the scope of the code from the [Setup](#Setup) section.

## Notion.get()

The `get()` method can be used to get any column from the Notion database and is used as follows:

```python
column_name = 'Name'
Names = N.get('Name')
```

This will return a `list` of all the elements in the `'Name'` column and store the value in `Names`.

**This function currently only supports `Title`, `Text`, `Number`, `Date`, `Select`, and `Rollup` column types**

## Notion.index()

The `index()` method can be used to get the corresponding value of another column, given an index column and value.

Consider the following database.

### Table 1

| Name   | Number | Text   |
|--------|--------|--------|
| Item 1 | 14     | Turkey |
| Item 2 | 16     | Bacon  |
| Item 3 | 18     | Club   |

If the `Name` column is used as the index column, `Item 2` is used as the index value, and the `Text` column is chosen as the target column:

```python
value = N.index(index_column_name='Name', 
                index_value='Item 2', 
                target_column_name='Text'
                )
```
Alternatively, this can be written as:
```python
value = N.index('Name', 'Item 2', 'Text')
```

`value` will be equal to `'Bacon'`.

# Changing Data

The following methods can be used to edit the database. 
These are written in the scope of the code from the [Setup](#Setup) section.

## Notion.set()

This method is used to change the value of a property, using the title as an index. It currently supports the `Title`, `Text`, `Number`, `Date`, and `Select` properties are supported. 
The type of the column is automatically determined by the client.

For example, consider **Table 1**. To change the `Number` column's value for `Item 3` to `Sandwich`, the following code would be used:

```python
N.set(index='Item 3',
      column_name='Number',
      value='Sandwich'
      )
```

Alternatively, this can be written as:

```python
N.set('Item 3', 'Number', 'Sandwich')
```

Furthermore, instead of using the name as an index, the integer value of the index can be used as well as follows. **The integer index may not be in the order as seen on the Notion interface. Check the `Title` column inside Python beforehand using the get() function.**
```python
N.set(2, 'Number', 'Sandwich')
```

This will change the database to the following:

### Table 2

| Name   | Number | Text     |
|--------|--------|----------|
| Item 1 | 14     | Turkey   |
| Item 2 | 16     | Bacon    |
| Item 3 | 18     | Sandwich |

### Bulk Edits

This method also supports bulk edits. Multiple indices can be changed to one value at the same time. For example:

```python
indices = [1, 5, 9]
N.set(indices, 'Column Name', 'Value')
```


## Notion.delete()

This method can be used to delete a row, using the title as an index. 
For example, the following code will delete the row at `Item 2` from **Table 2**:

**Use this method carefully, as data cannot yet be restored from a file.**

```python
N.delete('Item 2')
```

Giving the following database:

| Name   | Number | Text     |
|--------|--------|----------|
| Item 1 | 14     | Turkey   |
| Item 3 | 18     | Sandwich |

# Saving Data

## Notion.save()

This method can be used to create a JSON file of the database. 
Future versions will include an option to restore the database from a JSON file.