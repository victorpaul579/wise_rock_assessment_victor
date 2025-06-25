import pandas as pd
from pathlib import Path
from typing import Dict, Tuple

# Import the settings object to get the data directory path
from src.config import settings

class CsvExtractor:
    """
    A class to handle the extraction of data from CSV files.
    """

    def __init__(self, data_dir: Path):
        """
        Initializes the CsvExtractor with the directory containing the data files.

        Args:
            data_dir (Path): The path to the directory where CSV files are stored.
        """
        self.data_dir = data_dir
        if not self.data_dir.is_dir():
            raise FileNotFoundError(f"Data directory not found at: {self.data_dir}")

    def _generate_table_name(self, file_path: Path) -> str:
        """
        Generates a structured table name from a CSV file name.
        Example: 'ac_property.csv' -> 'stg_aries__ac_property'
        Example: 'completiontb.csv' -> 'stg_pro_count__completiontb'
        """
        file_name = file_path.stem
        
        if file_name == "ac_property":
            source_system = "aries"
        else:
            source_system = "pro_count"
            
        return f"stg_{source_system}__{file_name}"

    def extract_all(self) -> Dict[str, pd.DataFrame]:
        """
        Finds all CSV files, reads them, and returns a dictionary mapping
        the target table name to its corresponding pandas DataFrame.

        This allows the orchestrator to control the processing order.

        Returns:
            A dictionary where keys are table names and values are DataFrames.
        """
        print(f"Starting extraction from directory: {self.data_dir}")
        data_map = {}
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"Warning: No CSV files found in {self.data_dir}")
            return data_map

        for file_path in csv_files:
            try:
                print(f"--> Reading file: {file_path.name}")
                df = pd.read_csv(file_path)
                table_name = self._generate_table_name(file_path)
                data_map[table_name] = df
            except Exception as e:
                print(f"Error reading file {file_path.name}: {e}")
                continue
        
        print("Extraction complete.")
        return data_map

# Create a single, reusable extractor instance for our application.
csv_extractor = CsvExtractor(data_dir=settings.DATA_DIR)
