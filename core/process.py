import os
import pandas as pd
import logging as log
import core.utils as utils

log.basicConfig(level=log.INFO, format='%(asctime)s %(levelname)s %(message)s')
seasons = {}
bookmakers_1x2 = ['B365', 'BS', 'BW', 'GB', 'IW', 'LB', 'PS', 'SB', 'SJ', 'SY', 'VC', 'WH']


class DataFile:
    def __init__(self, filepath):
        self.name = os.path.basename(filepath)
        self.path = filepath
        self.tmp_path = ""
        filename_chunks = self.name.split('_')
        self.season = filename_chunks[1]

        if self.season[0] == '9':
            self.century = '1900'
        else:
            self.century = '2000'

        self.league = filename_chunks[2]

    def get_key(self):
        return self.century + '_' + self.season

    def get_tmp_name(self):
        return self.century + '.' + self.season + '.csv'


def collapse(row_data, list_columns, column_postfix):
    """Given a row of a datafile and a list of its columns,
    takes in order the value of each column and returns the first one that is not empty"""
    if column_postfix is None:
        column_postfix = ""

    for column in list_columns:
        try:
            if row_data[column + column_postfix] is not None:
                return row_data[column + column_postfix]
        except KeyError:
            continue

    return None


def process_country(country_name):
    """Process al datafiles for a given country producing csv files in the tmp directory"""
    log.info('Processing country ' + country_name)

    country_tmp_path = os.path.join(utils.tmp_path, country_name)
    utils.replace_directory(country_tmp_path)

    for data_file in os.listdir(os.path.join(utils.input_path, country_name)):
        process_data_file(os.path.join(utils.input_path, country_name, data_file), country_name)

    log.info('Country ' + country_name + ' has been processed')


def process_data_file(file_path, country_name):
    """For a datafile it creates a corresponding csv in the tmp directory of its league.
    The new csv contains only a few selected columns and some calculated variables."""
    df = pd.read_csv(file_path)
    df = df.reset_index()
    df['VirtualWeek'] = 0
    df['H'] = None
    df['D'] = None
    df['A'] = None

    league_map = {}

    for index, row in df.iterrows():
        update_virtual_week(row['HomeTeam'], league_map)
        league_map[row['AwayTeam']] = league_map[row['HomeTeam']]
        df.at[index, 'VirtualWeek'] = league_map[row['HomeTeam']]
        df.at[index, 'H'] = collapse(row, bookmakers_1x2, 'H')
        df.at[index, 'D'] = collapse(row, bookmakers_1x2, 'D')
        df.at[index, 'A'] = collapse(row, bookmakers_1x2, 'A')

    data_file = DataFile(file_path)

    league_path = os.path.join(os.path.join(utils.tmp_path, country_name), data_file.league)

    if data_file.get_key() not in seasons:
        seasons[data_file.get_key()] = []

    data_file.tmp_path = os.path.join(league_path, data_file.get_tmp_name())
    seasons[data_file.get_key()].append(data_file)
    df = df[df['Div'].notna()]

    utils.create_directory(league_path)
    df.to_csv(
        data_file.tmp_path,
        columns=['Div', 'VirtualWeek', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'H', 'D', 'A'],
        index=False
    )


def update_virtual_week(team, league_map):
    """Increments the counter in the league_map for the given team"""
    if team not in league_map:
        league_map[team] = 1
    else:
        league_map[team] += 1


def merge(season_key):
    """Merges datafiles related to the same season from different leagues into a single csv file
    within the "data" directory"""
    sf = pd.DataFrame()
    for data_file in seasons[season_key]:
        sf = pd.concat([sf, pd.read_csv(data_file.tmp_path)])

    sf.to_csv(os.path.join(utils.data_path, season_key + '.csv'), index=False)


def process():
    """Prepares data raw data for the backtester. At the end of this function the data directory should be filled.
    This function could be used multiple times without deleting data directory."""
    log.info('Start')
    log.info('Base path:' + utils.base_path)
    log.info('Input path:' + utils.input_path)
    log.info('Temp path:' + utils.tmp_path)
    log.info('Data path:' + utils.data_path)

    utils.replace_directory(utils.tmp_path)

    log.info('Processing input files...')

    for path in os.listdir(utils.input_path):
        if os.path.isdir(os.path.join(utils.input_path, path)):
            process_country(path)

    log.info('All input files have been processed')

    sorted_seasons = sorted(seasons.keys())
    utils.replace_directory(utils.data_path)

    log.info('Processing seasons...')
    for season in sorted_seasons:
        log.info('Processing season ' + season)
        merge(season)
        log.info('Season ' + season + ' has been processed')

    log.info('All seasons have been processed')
    utils.replace_directory(utils.tmp_path)
    log.info('End')
