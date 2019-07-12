## What is this?

TextPack efficiently groups similar values in large (or small) data sets. Under the hood, it builds a document term matrix of n-grams assigned a TF-IDF score. It then uses matrix multipcation to quickly calculate the cosine similarity between these values. For a technical explination, [check out this blog post](https://medium.com/p/2493b3ce6d8d).

If you've ever had a spreadsheet, SQL table or JSON string filled with inconsistent inputs like this:

| row |     fullname      |
|-----|-------------------|
|   1 | John F. Doe       |
|   2 | Esquivel, Mara    |
|   3 | Doe, John F       |
|   4 | Whyte, Luke       |
|   5 | Doe, John Francis |

and weanted to perform some kind of analysis – perhaps in a Pivot Table or a Group By statement – you can use TextPack to comb hundreds or thousands of cells in seconds and circumvent slight deviations in spelling and formatting by creating a third column like this:

| row |     fullname      |  name_groups  |
|-----|-------------------|---------------|
|   1 | John F. Doe       | Doe John F    |
|   2 | Esquivel, Mara    | Esquivel Mara |
|   3 | Doe, John F       | Doe John F    |
|   4 | Whyte, Luke       | Whyte Luke    |
|   5 | Doe, John Francis | Doe John F    |

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

## How do I use it?

#### Installation

```
pip install textpack
```

#### Import data

Import the module first:

```
from textpack import tp
```

#### Instantiate TextPack

*tp.Textpack(df, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)*

The TextPack class accepts the following parameters:

 - `df` (required): A Pandas' DataFrame containing the dataset to group
 - `columns_to_group` (required): A list or string matching the column headers you'd like to clean and group
 - `match_threshold`: This is a floating point number between 0 and 1 that represents the cosine similarity threshold we'll use to determine if two strings should be grouped. The closer the threshold to 1, the higher the similarity will need to be.
 - `ngram_remove`: A regular expression you can use to filter characters out of your strings when we build n-grams
 - `ngram_length`: The length of our n-grams. This should be used in tandem with `match_threshold` to find the best approach for grouping your dataset. Also, if you find TextPack is running slow, you might consider raising the n-gram length.

TextPack can also be instantiated using the following helper methods, each of which is just a wrapper that converts a data format to a Pandas DataFrame and then passes it to TextPack. Thus, they all require a file path and `columns_to_group`, and take the same three optional parameters as TextPack.

*tp.read_csv(csv_path, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)*

*tp.read_excel(excel_path, columns_to_group, sheet_name=None, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)*

*tp.read_json(json_path, columns_to_group, match_threshold=0.75, ngram_remove=r'[,-./]', ngram_length=3)*

#### Run Textpack and group values

TextPack objects have the following public properties:

 - `df`: The dataframe used internally by TextPack, manipulate as you see fit
 - `group_lookup`: A Python dictionary used to reference each value that has a group. Eg: 

```
{ 
    'John F. Doe': 'Doe John F',
    'Doe, John F': 'Doe John F',
    'Doe, John Francis': 'Doe John F'
}
```

Objects have the following public methods:

 - `build_group_lookup()`: Runs the cosine similarity analysis and builds `group_lookup`.
 - `add_grouped_column_to_data(column_name='Group')`: Uses vectorization map values to groups via `group_lookup` and add the new group column to the DataFrame. the column header can be set via `column_name`.
 - `set_match_threshold(match_threshold)`: Modify the match threshold internally.
 - `set_ngram_remove(ngram_remove)`: Modify the n-gram regex filter internally.
 - `set_ngram_length(ngram_length)`: Modify the n-gram length internally.
 - `run(column_name='Group')`: A helper function that runs `build_group_lookup` followed by `add_grouped_column_to_data`.

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

I wrote [this detailed blog post](https://medium.com/p/2493b3ce6d8d) to explian how TextPack works behind the scene and why it is super fast. Check it out!