from io import StringIO

import pandas as pd


def df_from_markdown(_markdown_table: str) -> pd.DataFrame:
    """
    Convert a Markdown table to a pandas DataFrame.
    :param _markdown_table: A Markdown table as a string.
    :return: A pandas DataFrame.
    """
    df = pd.read_csv(StringIO(_markdown_table.replace("|", "")),
                     sep=r'\s{2,}',
                     engine='python')
    if 'Source' in df.columns:
        df = df.drop(columns='Source')
    return df
