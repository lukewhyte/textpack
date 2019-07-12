## What is this?

TextPack efficiently groups similar values in large (or small) datasets. Under the hood, it builds a document term matrix of n-grams assigned a TF-IDF score. It then uses matrix multiplication to quickly calculate the cosine similarity between these values. For a technical explination, [I wrote a blog post](https://medium.com/p/2493b3ce6d8d).

## Why do I care?

If you're a analyst, journalist, data scientist or similar and ever had a spreadsheet, SQL table or JSON string filled with inconsistent inputs like this:

| row |     fullname      |
|-----|-------------------|
|   1 | John F. Doe       |
|   2 | Esquivel, Mara    |
|   3 | Doe, John F       |
|   4 | Whyte, Luke       |
|   5 | Doe, John Francis |

And you've wanted to perform some kind of analysis – perhaps in a Pivot Table or a Group By statement – but are hindered by the deviations in spelling and formatting, you can use TextPack to comb hundreds to thousands of cells in seconds and create a third column like this:

| row |     fullname      |  name_groups  |
|-----|-------------------|---------------|
|   1 | John F. Doe       | Doe John F    |
|   2 | Esquivel, Mara    | Esquivel Mara |
|   3 | Doe, John F       | Doe John F    |
|   4 | Whyte, Luke       | Whyte Luke    |
|   5 | Doe, John Francis | Doe John F    |

We can then group by `name_groups` and perform our analysis. 

You can also group across multiple columns. For instance, given the following:

| row |  make  |   model   |
|-----|--------|-----------|
|   1 | Toyota | Camry     |
|   2 | toyta  | camry DXV |
|   3 | Ford   | F-150     |
|   4 | Toyota | Tundra    |
|   5 | Honda  | Accord    |

You can group across `make` and `model` to create:

| row |  make  |   model   |  car_groups  |
|-----|--------|-----------|--------------|
|   1 | Toyota | Camry     | toyotacamry  |
|   2 | toyta  | camry DXV | toyotacamry  |
|   3 | Ford   | F-150     | fordf150     |
|   4 | Toyota | Tundra    | toyotatundra |
|   5 | Honda  | Accord    | hondaaccord  |

Boom.

## How do I use it?

#### Installation

```
pip install textpack
```

#### Import module

```
from textpack import tp
```

#### Instantiate TextPack

```
tp.Textpack(df, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)
```

Class parameters:

 - `df` (required): A Pandas' DataFrame containing the dataset to group
 - `columns_to_group` (required): A list or string matching the column headers you'd like to parse and group
 - `match_threshold` (optional): This is a floating point number between 0 and 1 that represents the cosine similarity threshold we'll use to determine if two strings should be grouped. The closer the threshold to 1, the higher the similarity will need to be.
 - `ngram_remove` (optional): A regular expression you can use to filter characters out of your strings when we build our n-grams
 - `ngram_length` (optional): The length of our n-grams. This can be used in tandem with `match_threshold` to find the sweet spot for grouping your dataset. If TextPack is running slow, it's usually a sign to consider raising the n-gram length.

TextPack can also be instantiated using the following helpers, each of which is just a wrapper that converts a data format to a Pandas DataFrame and then passes it to TextPack. Thus, they all require a file path, `columns_to_group` and take the same three optional parameters as callin `TextPack` directly.

```
tp.read_csv(csv_path, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)
```

```
tp.read_excel(excel_path, columns_to_group, sheet_name=None, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)
```

```
tp.read_json(json_path, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)
```

#### Run Textpack and group values

TextPack objects have the following public properties:

 - `df`: The dataframe used internally by TextPack – manipulate as you see fit
 - `group_lookup`: A Python dictionary built by `build_group_lookup` and then used by `add_grouped_column_to_data` to lookup each value that has a group. It looks like this: 

```
{ 
    'John F. Doe': 'Doe John F',
    'Doe, John F': 'Doe John F',
    'Doe, John Francis': 'Doe John F'
}
```

Textpack objects also have the following public methods:

 - `build_group_lookup()`: Runs the cosine similarity analysis and builds `group_lookup`.
 - `add_grouped_column_to_data(column_name='Group')`: Uses vectorization to map values to groups via `group_lookup` and add the new `Group` column to the DataFrame. The column header can be set via `column_name`.
 - `set_match_threshold(match_threshold)`: Modify the match threshold internally.
 - `set_ngram_remove(ngram_remove)`: Modify the n-gram regex filter internally.
 - `set_ngram_length(ngram_length)`: Modify the n-gram length internally.
 - `run(column_name='Group')`: A helper function that calls `build_group_lookup` followed by `add_grouped_column_to_data`.

 #### Export our grouped dataset

  - `export_json(export_path)`
  - `export_csv(export_path)`

#### A simple example

```
from textpack import tp

cars = tp.read_csv('./cars.csv', ['make', 'model'], match_threshold=0.8, ngram_length=5)

cars.run()

cars.export_csv('./cars-grouped.csv')
```

## How does it work?

As mentioned above, under the hood, we're building a document term matrix of n-grams assigned a TF-IDF score. We're then using matrix multipcation to quickly calculate the cosine similarity between these values.

I wrote [this detailed blog post](https://medium.com/p/2493b3ce6d8d) to explian how TextPack works behind the scene and why it's fast. Check it out!