import pandas as pd
import numpy as np
import csv
from docx import Document


def docx_to_csv(doc_path, csv_path, mode='w'):
    """
    Read tables from docx document to csv without preprocessing
    
    Parameters:
        doc_path:  path to docx document (read)
        csv_path:  path to csv document (save)
        mdoe:      open file mode: 'w' - write; 'a' - append
    """
    doc = Document(doc_path)
    
    with open(csv_path, mode) as f:
        writer = csv.writer(f)
        for table in doc.tables:
            for row in table.rows:
                # replacing '\n' makes 'PRE-CONDITION' fit on single line
                # end evoids error while spliting row
                writer.writerow(cell.text.replace('\n', '|n').strip(' |n')
                                for cell in row.cells)
            
            writer.writerow(['TABLE_END'])
            

class TableProcessor:
    def __init__(self, raw_data, countries_df=False, clean_df=False, pre_df=False, country=False):
        self.table_name_col = 'CONNECTION TYPE'
        self.country_col = 'COUNTRY'
        self.pre_col = 'PRE-CONDITION'
        self.table_end = 'TABLE_END'
        
        self.rdf = pd.read_csv(raw_data, header=None, sep='\n')
        self.cdf = clean_df if clean_df else pd.DataFrame()
        self.pre_df = pre_df if pre_df else pd.DataFrame()
        self.pre_id = False
        self.countries_df = (countries_df 
                             if isinstance(countries_df, pd.DataFrame) 
                             else pd.DataFrame({'id':[0], self.country_col:[None]}))
        self.country=country
        
        # TODO
        # fix country setup when given 'country' argument
#         self.set_country_id() 
        
        
    def process_tables(self):
        rows = csv.reader(self.rdf[0])
        
        for row in rows:
            
            if self.is_table_end(row):
                self.reset(row)
            
            elif self.is_country(row):
                self.set_country(row)
            
            elif self.is_table_name(row):
                self.set_table_name(row)
                
            elif self.is_table_header(row):
                self.set_table_header(row)
                
            elif self.is_precondition(row):
                self.set_precondition(row)
                
            else:
                self.set_row(row)
                
        self.handle_outcome()
        return self.cdf, self.countries_df, self.pre_df
    
    # RESET
    
    def is_table_end(self, row):
        return row[0] == self.table_end
    
    def reset(self, row):
        self.pre_id = False
    
    # COUNTRY
    def is_country(self, row):
        return row[0].startswith('COUNTRY')
    
    def set_country(self, row):
        if not self.country:
            self.country = row[0].split(':')[1].strip()
            self.set_country_id()
            
    def set_country_id(self):        
        if self.country in self.countries_df[self.country_col].values:
            mask = self.countries_df[self.country_col] == self.country
            self.country_id = self.countries_df[mask].id.values[0]
        else:
            self.country_id = self.countries_df['id'].max() + 1
            new_country = {'id': self.country_id, 
                           self.country_col: self.country}
            self.countries_df = self.countries_df.append(new_country, 
                                                         ignore_index=True)
    # TABLE NAME
    def is_table_name(self, row):
        return len(row) > 1 and len(set(row)) == 1 and all(map(str.isupper, row))
    
    def set_table_name(self, row):
        self.table_name = row[0]
    
    # TABLE HEADER
    def is_table_header(self, row):
        return all(map(str.isupper, row))
    
    def set_table_header(self, row):
        self.columns = {idx: column for idx, column in enumerate(row)}
        for column in self.columns.values():
            if column not in self.cdf.columns:
                self.cdf[column] = np.nan
                
    # PRE-CONDITION
    def is_precondition(self, row):
        return row[0].startswith('PRE-CONDITION')        
    
    def set_precondition(self, row):
        self.pre_id = 1
        new_precondition = {
            'id': self.pre_id, 
            self.pre_col: row[0],
        }
        if len(self.pre_df):
            self.pre_id = self.pre_df['id'].max() + 1
            new_precondition['id'] = self.pre_id
            self.pre_df = self.pre_df.append(new_precondition, 
                                             ignore_index=True)
        else:
            self.pre_df = self.pre_df.append(new_precondition, 
                                             ignore_index=True)
    
    # TABLE ROW OF DATA
    def set_row(self, row):
        self.check_country()
        
        dict_row = {self.columns[col_id]: val for col_id, val in enumerate(row)}
        dict_row[self.table_name_col] = self.table_name
        dict_row[self.country_col] = self.country_id
        if self.pre_id:
            dict_row[self.pre_col] = self.pre_id
        
        self.cdf = self.cdf.append(dict_row, ignore_index=True)
        
    # OUTCOME, SCENARIO
    def handle_outcome(self):
        self.merge_scenarios()
        self.clean_outcome_value()
        
    def merge_scenarios(self):
        id_vars = [c for c in self.cdf.columns if not c.endswith('SCENARIO')]
        self.cdf = self.cdf.melt(id_vars=id_vars)
        self.cdf.rename(columns={'value': 'OUTCOME', 
                                 'variable': 'SCENARIO'}, inplace=True)
    
    def clean_outcome_value(self):
        not_outcome = self.cdf.columns.drop('OUTCOME').tolist()
        
        self.cdf = self.cdf.set_index(not_outcome)['OUTCOME']\
            .str.split('\|n', expand=True)\
            .stack().reset_index()\
            .rename(columns={0:'OUTCOME'})\
            .loc[:, self.cdf.columns]
    
    # OTHER
    def check_country(self):
        try:
            self.country_id
        except AttributeError as e:
            e.args = (('Country not found! '
                      'Please check input document,'
                      'or pass country as an argument'), *e.args)
            raise 
    