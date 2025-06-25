import pandas as pd

class Transformer:
    """
    A class dedicated to performing data transformations.
    This class can be expanded with more methods for cleaning,
    standardizing, or enriching data as needed.
    """

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes all column names in a DataFrame to lowercase.
        """
        df_copy = df.copy()
        df_copy.columns = [col.lower() for col in df_copy.columns]
        return df_copy

    def transform_completion_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies specific transformations for the completiontb dataset.

        - Converts the 'activeflag' column from integer (1/0) to boolean (True/False).
        
        This is a great example of a targeted transformation to fix a
        data type mismatch between source and destination.

        Args:
            df (pd.DataFrame): The input DataFrame from completiontb.csv.

        Returns:
            pd.DataFrame: The transformed DataFrame, ready for loading.
        """
        df_transformed = df.copy()

        # Check if the 'activeflag' column exists before trying to transform it
        if 'activeflag' in df_transformed.columns:
            print("--> Transforming 'activeflag' column to boolean.")
            # Convert the column to integer type first to handle any potential
            # floating point issues (e.g., 1.0), then cast to boolean.
            df_transformed['activeflag'] = df_transformed['activeflag'].astype(int).astype(bool)
        
        return df_transformed

# Create a single, reusable transformer instance for our application.
transformer = Transformer()
