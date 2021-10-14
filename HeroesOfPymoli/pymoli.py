import pandas as pd
# this script was used to create the code that ended up in the jupyter notebook
# region
# natively display more info in pandas
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
# endregion


# region

def spaceless_lowers(dataframe):
    """
    :param dataframe: a dataframe with columns that have spaces and uppercase letters
    :return: a dataframe with the spaces replaced with _ and all caps made lowercase.
    """
    try:
        cols = dataframe.columns
        cols = [col.replace(' ', '_').lower() for col in cols]
        dataframe.columns = cols

        return dataframe

    except NameError:
        print('There is an unresolved reference to the dataframe in the function\'s argument.\n'
              'Make sure that the dataframe has been read and defined.')


def format_money(values):
    """
    :param values: iterable object you want to convert to money format
    :return: the values formatted as money
    """
    try:
        formatted_values = ['${:,.2f}'.format(value) for value in values]
        return formatted_values
    except TypeError as e:
        print('you must pass an iterable to this function.')


def format_percent(values):
    """
    :param values: iterable object you want to convert to percent format
    :return: values formatted as percent
    """
    try:
        formatted_values = ['{:.2%}'.format(value) for value in values]
        return formatted_values

    except TypeError as e:
        print('you must pass an iterable to this function.')


def make_the_output(df, *col_to_group):
    # remove spaces and caps from df so its easier to work with
    # df = spaceless_lowers(df)

    dict_to_print = dict()

    unique_players = df['sn'].nunique()  # 576

    unique_items = df['item_id'].nunique()  # 179
    avg_price = df['price'].mean()  # 3.05
    num_purchases = len(df['purchase_id'])  # 780
    total_revenue = df['price'].sum()  # 2379.77

    # ! return
    unique_df = pd.DataFrame({'Total Players': [unique_players]})

    dict_to_print['unique_df'] = unique_df

    # ! return
    purch_df = pd.DataFrame(
            {
                    'Unique Items': unique_items,
                    'Average Price': format_money([avg_price]),
                    'Total Purchases': [num_purchases],
                    'Total Revenue': format_money([total_revenue])
            }
    )

    dict_to_print['purchase_df'] = purch_df

    # removing this print statement from the real script
    # so i can easily move it to a notebook
    # print(
    #         f'Player Count\n'
    #         f'{unique_df}\n\n'
    #         f'Purchasing Analysis\n'
    #         f'{purch_df}\n\n'
    # )

    # instantiate the dictionary used later in the loop
    output_dict = dict()

    # name of the bin categories
    cats = '<10 10-14 15-19 20-24 25-29 30-34 35-39 >40'.split()

    # upper bound of each bin
    b = [0, 9, 14, 19, 24, 29, 34, 39, 100]

    # reassigning this column so as to prevent naming conflicts when
    # passing column names as parameters
    df['age_new'] = df['age']

    # binning ages and reassigning the bin name to the age column
    df['age'] = pd.cut(df['age_new'], bins=b, labels=cats)

    # loop through each column name passed to function
    for group in col_to_group:
        # gbo is standard naming for groupby objects
        gbo = df.groupby(group)
        purchase_count = gbo['purchase_id'].count()
        avg_purch_price = gbo['price'].mean()
        total_purch_value = gbo['price'].sum()
        unique_per_group = gbo['sn'].nunique()
        avg_total_per_person = total_purch_value / unique_per_group

        pct_players = unique_per_group / unique_players

        # ! return
        players_df = pd.DataFrame(
                {
                        'Total Count': unique_per_group,
                        'Percentage': format_percent(pct_players)
                }
        )

        # ! return
        purch_group_df = pd.DataFrame(
                {
                        'Purchase Count': purchase_count,
                        'Average Purchase Price': format_money(avg_purch_price),
                        'Total Purchase Value': format_money(total_purch_value),
                        'Average Total Purchase per Person': format_money(avg_total_per_person)
                }
        )

        # adding each dataframe to the dictionary instantiated above.
        # format is {groupname:[dfs made for each groupname]}
        output_dict[group] = [players_df, purch_group_df]

    return output_dict, dict_to_print


# endregion


# path of csv file to read
path = 'purchase_data.csv'
df = spaceless_lowers(pd.read_csv(path))


# calling and assigning the function
a, b = make_the_output(df, 'gender', 'age')

# loop through each key and print all dfs in dict's values
for k in a.keys():
    for i in range(len(a[k])):
        print(f'{a[k][i]}\n\n')


spenders = df.groupby('sn').agg(
        {
                'purchase_id': 'count',
                'price': ['mean', 'sum']
        }
).droplevel(0, axis=1)

spenders = spenders.nlargest(5, 'sum')

for c in ['mean', 'sum']:
    spenders[c] = spenders[c].apply('${:,.2f}'.format)


s = df.groupby(['item_id', 'item_name']).agg(
        {
                'item_id': 'count',
                'price': ['mean', 'sum']
        }
)

s.sort_values(('item_id', 'count'), ascending=False, inplace=True)

most_popular = s.nlargest(5, ('item_id', 'count'))
most_profit = s.nlargest(5, ('price', 'sum'))

for _ in [most_popular, most_profit]:
    for c in ['mean', 'sum']:
        _[('price', c)] = _[('price', c)].apply('${:,.2f}'.format)

print(most_popular)
print(most_profit)
