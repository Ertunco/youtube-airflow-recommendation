import yaml
import argparse
import sys
sys.path.append("path/to/parent/folder")
import video_picker as vp


def load_yaml(filepath):
    """Import YAML config file."""
    with open(filepath, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def run_youtube_etl():
    search_term = "Experian"
    search_period = 7
    config = load_yaml('./config.yaml')
    start_date_string = vp.get_start_date_string(search_period)
    df = vp.search_each_term(search_term, config['api_key'], start_date_string)
    print("ETL completed successfully")

