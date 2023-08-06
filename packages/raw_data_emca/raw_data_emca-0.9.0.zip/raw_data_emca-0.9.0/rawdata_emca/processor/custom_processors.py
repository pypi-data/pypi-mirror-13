'''
Created on Jan 11, 2016

@author: id19868
'''
from rawdata_emca.processor import BaseProcessor
from rawdata_emca.runner.config_entry import ConfigEntry
import datetime
import os
import csv
import shutil
from rawdata_emca.utilities import RawDataUtilities
from rawdata_emca.utilities import csvsort
from rawdata_emca.processor.built_in import TwoFileProcessor
from rawdata_emca.errors.data_error import RawDataError

class merge_files(BaseProcessor):
    ''' this class merges the contents of multiple files and only keeps 1 version of each record
    
    The files are read in order and the key is specified for each file.. 
    The idea is that you want to keep only 1 version of the truth and the first file to have it.. has the truth
    
    name the files in order: file1, file2, file3, etc..
    then add the keys (comma seperated list) file1_key, file2_key, file3_key, etc..
        (if no key is found for a file (other than file1), then the key is assumed to be the same as file1)
    
    Then if you only want a subset of columns then use parameters like the following: file1_col_fielda, file1_col_fieldb, the (fielda and fieldb) are the 
    columns from the file that you want.. the value is the renamed column.. (optional) 
    
    The header is assumed to be the same as the first file, unless passed in otherwise from a parameter
    '''
    def execute_processor(self):
        # {filename:{csv:...,reader:...},...
        self.file_dict = {}
        self.load_up_params()
        self.set_header()
        self.open_files()
        main = 'file1' # this should be the main file we are concerned about, has the latest records
        self.setup_csv_temp_writer(self.get_temp_csv_name(), self.out_header, write_header=True)
        # first go through each file and read the first record
        for f in range(len(self.file_dict.keys())):
            fn = f + 1
            fname = 'file'+str(fn)
            print "starting file: "+fname
            self.read_file(fname, True)
        
        while self.keep_going():
            write_main = True
            for x in range(1,self.num_files):
                fname = 'file'+str(x+1)
                comp = self.compare_to_main(fname)
                if comp == 0:
                    write_main = False
                    self.read_file(fname)
                elif comp < 0:
                    write_main = False
                    self.write_record(fname)
                    self.read_file(fname)
            if write_main:
                self.write_record(main)
                self.read_file(main)
        
            
        self.close_temp_csv()      
        return 0
    
    def keep_going(self):
        for x in range(self.num_files):
            fname = 'file'+str(x+1)
            if self.file_dict[fname]['last_read']:
                return True
        
        return False
    def compare_to_main(self, fname):
        in_key = self.file_dict[fname]['last_read_key']
        main_key = self.file_dict['file1']['last_read_key']
        
        if not main_key:
            if not in_key:
                return 0
            else:
                return -1
        
        if not in_key:
            return 1
        
        if in_key < main_key:
            return -1
        elif in_key == main_key:
            return 0
        else:
            return 1        
    
    def write_record(self, fname):
        in_rec = self.file_dict[fname]['last_read']
        if in_rec:
            cols = self.file_dict[fname]['cols']
            rec_dict = {}
            if cols:
                for col in cols.keys():
                    rename = cols[col]
                    if len(rename.strip()) == 0:
                        rename = col
                    rec_dict[rename] = in_rec[col]
            else:
                rec_dict = in_rec
            
            self.write_temp_rec(rec_dict)
            
    
    
    def open_files(self):
        ''' input is a dictionary of files {'file1':'c:/temp.csv','file2':'C:/temp2.csv'} '''
        for a_file in self.file_dict.keys():
            name = self.file_dict[a_file]['name']
            self.file_dict[a_file]['csv'] = open(name)
            self.file_dict[a_file]['reader'] = csv.DictReader(self.file_dict[a_file]['csv'])
            self.file_dict[a_file]['header'] = self.file_dict[a_file]['reader'].fieldnames
    
    def read_next(self,file_name):
        rec = self.file_dict[file_name]['reader'].next()
        self.file_dict[file_name]['last_read'] = rec
        self.file_dict[file_name]['last_read_key'] = self.get_key(rec, file_name)
        # check for empty record
        if not self.file_dict[file_name]['last_read_key']:
            self.read_next(file_name)
 
    def read_file(self, file_name, first = False):    
        if first:
            self.read_next(file_name)
        else:
            if self.file_dict[file_name]['last_read']:
                try:
                    self.read_next(file_name)
                except StopIteration:
                    self.file_dict[file_name]['last_read']  = None
                    self.file_dict[file_name]['last_read_key'] = None
                    print 'Finished reading: '+file_name

        if not self.file_dict[file_name]['last_read'] :
            if not self.file_dict[file_name]['csv'].closed:
                self.file_dict[file_name]['csv'].close()
            
        return self.file_dict[file_name]['last_read']
    
    def get_key(self, in_rec, fname):
        keys = self.file_dict[fname]['key'].split(",")
        ret_key = ""
        
        for k in keys:
            ret_key = ret_key+in_rec[k]
            
        return ret_key
    
    def load_up_params(self):
        if "file1" not in self.param_dict.keys():
            raise RawDataError("Required field 'file1' is missing, must have at least 2 files to use this processor")
        
        if "file2" not in self.param_dict.keys():
            raise RawDataError("Required field 'file2' is missing, must have at least 2 files to use this processor")
        
        self.out_header = self.param_dict.get('header',None)
        
        keep_going = True
        file_num = 1
        while keep_going:
            fname = 'file'+str(file_num)

            if fname in self.param_dict.keys():
                filepath = self.param_dict[fname]
                rec_key = self.param_dict[fname+"_key"]
                
                cols = None
                for key in self.param_dict.keys():
                    prefix = fname+"_col_"
                    if key.startswith(prefix):
                        col = key[len(prefix):]
                        rename = self.param_dict[key]
                        if not cols:
                            cols = {col:rename}
                        else:
                            cols[col] = rename
                
                    
                self.file_dict[fname] = {'name':filepath,'csv': None, 'key':rec_key,'cols':cols,'reader': None, 'last_read':None, 
                                         'header':None, 'last_read_key':None}
                file_num = file_num + 1
            else:
                keep_going = False
                self.num_files = file_num - 1
            
    def set_header(self):
        
        if not self.out_header:
            self.out_header = self.file_dict['file1']['header']
        else:
            self.out_header = self.out_header.split(",")

class filter_file(BaseProcessor):
    ''' given a file file, select only those that match the given criteria 
        
        match criteria:  equal, gt (greater than), lt (less than), gte (greater than or equal, lte (less than or equal), 
                in (comma seperated list)
        column name follows
        equal_type = Estimate
        
        for dates add _dt at the end of the key
        
        gt_report_date_dt = 01/01/2015
        
        the value provided is the match against criteria
    '''
    def _equal(self,val,comp): return val == comp
    def _gt(self,val,comp): return val > comp
    def _gte(self,val,comp): return val >= comp
    def _lt(self,val,comp): return val < comp
    def _lte(self,val,comp): return val <= comp
    def _in(self, val, comp): return val in comp
    
    func_list = [float,int,str]
    
    def load_filters(self):
        crit_list = {'equal':self._equal,'gt':self._gt,'lt':self._lt,'gte':self._gte,'lte':self._lte,'in':self._in}
        
        self.crit_dict = {}
        for param in self.param_dict.keys():
            criterion = param[:param.find('_')]
            if criterion in crit_list.keys():
                field = param[len(criterion)+1:]
                dt = False
                if field.endswith("_dt"):
                    dt = True
                    field = field[:-3]
                value = self.param_dict[param]
                
                if dt:
                    value = RawDataUtilities.date_from_string(value)
                else:
                    if criterion == 'in':
                        mlist = value.split(",")
                        value = [self.convert(m) if self.convert(m) else m for m in mlist]
                    else:
                        value = self.convert(value)
                    
                self.crit_dict[param] = {'field':field,'criterion':criterion,'value':value,'function':crit_list[criterion]}
    
    def convert(self, value):
        for func in self.func_list:
            nval = self.convertf(value,func)
            if nval:
                return nval
        return value
    
    def convertf(self, value, function):
        try:
            return function(value)
        except Exception:
            return None
    
    def matches_criteria(self, record):
        match = True
        for key in self.crit_dict.keys():
            criteria = self.crit_dict[key]   
            value = record[criteria['field']]
            if not criteria['function'](value, criteria['value']):
                match = False
            
        return match
        
    def execute_processor(self):
        
        filename = self.param_dict['file']
        filepath = os.path.join(self.entry.working_directory, filename)
        self.load_filters()
        
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            self.setup_csv_temp_writer(self.get_temp_csv_name(), reader.fieldnames, write_header=True)
            for row in reader:
                if self.matches_criteria(row):
                    self.write_temp_rec(row)
        self.close_temp_csv()
        return 0
    
class rename_file(BaseProcessor):
    ''' rename a file '''
    def execute_processor(self):
        current_file = self.param_dict['current_file']
        current_dir = self.param_dict['current_path']
        new_name = self.param_dict['new_name']
        filepath = os.path.join(current_dir, current_file)
        
        if os.path.isfile(filepath):
            os.remove(filepath)
        
        newpath = os.path.join(current_dir,new_name)
        os.rename(filepath, newpath)
        
        return 0
        
class move_file(BaseProcessor):
    ''' move one file to a new location '''
    def execute_processor(self):
        filename = self.param_dict['move_file']
        destination = self.param_dict['destination']
        
        full_path = os.path.join(self.entry.working_directory,filename)
        
        shutil.move(full_path, destination)
        
        return 0
class two_file_processor_dummy(TwoFileProcessor):


    def create_dummy_row(self, dummy_string):
        if dummy_string.upper().strip() == "NONE":
            return None
        
        if len(dummy_string.strip()) == 0:
            return None
        
        dummy_fields = dummy_string.split(",")
        dummy_row = {d.strip().split(":")[0]:d.strip().split(":")[1] for d in dummy_fields}
        return dummy_row
    
    def create_key_match(self):
        keys1 = self.file1_key.split(",")
        keys2 = self.file2_key.split(",")
        
        return {keys2[x]:keys1[x] for x in range(len(keys1))}
    
    def execute_processor(self):
        """
        Works the same as the built in two file processor.. but when there is no match, we add dummy records (comma seperated)
        
        pass them in like this key:value, key1:value1, key2:value2, etc..
        
        split by comma then by colon
        """
        
        # pull in the parameter that has the file names we will process
        filename1 = self.param_dict['file1']
        filename2 = self.param_dict['file2']
        
        ''' these next 2 lines are the ones that I added to create a dummy row '''
        right_dummy = self.create_dummy_row( self.param_dict['dummy_rec_right'])
        left_dummy = self.create_dummy_row( self.param_dict['dummy_rec_left'])
        
        
       

        self.open_files(os.path.join(self.entry.working_directory,filename1), os.path.join(self.entry.working_directory,filename2))
        self.process_params()
        key_dict = self.create_key_match()
        file1_rec = self.read_file1(first=True)
        file2_rec = self.read_file2(first=True)
        
        file2_used = False
        
        # call the convenience method to setup the temp_csv file.  This will also write the header row by default
        self.setup_csv_temp_writer(self.get_temp_csv_name(), self.get_header(self.file1_reader.fieldnames,self.file2_reader.fieldnames),preserve_order=True)
        
        while file1_rec:
            combined = {k:v for k,v in file1_rec.items()}
            if file2_rec and self.get_key(file2_rec,self.file2_key) == self.get_key(file1_rec,self.file1_key):
                # merge these two bad boys
                combined.update(self.get_values(file2_rec))
                file2_used = True
                ### WRITE ###
                self.write_temp_rec(combined)
                file1_rec = self.read_file1()
            elif file2_rec and self.get_key(file1_rec,self.file1_key) > self.get_key(file2_rec,self.file2_key):
                if not file2_used and left_dummy:
                    ''' left side dummy 
                    now use the already created dummy_row to updated the dictionary '''
                    left_dummy.update(self.get_values(file2_rec))
                    key_fields = {key_dict[k]:file2_rec[k] for k in self.file2_key.split(",")}
                    left_dummy.update(key_fields)
                    self.write_temp_rec(left_dummy)
                    left_dummy = self.create_dummy_row( self.param_dict['dummy_rec_left'])
                    
                    
                file2_rec = self.read_file2()
                file2_used = False
                
            elif not file2_rec or self.get_key(file1_rec,self.file1_key) < self.get_key(file2_rec,self.file2_key):
                ### WRITE REC WITH NO MATCH ###
                if self.keep_nomatch:
                    ''' right side dummy
                    now use the already created dummy_row to updated the dictionary '''
                    if right_dummy:
                        combined.update(self.get_values(right_dummy))
                    self.write_temp_rec(combined)
                file1_rec = self.read_file1()
            else:
                raise Exception
        self.close_temp_csv()
        return 0
    
class dup_counter(BaseProcessor):
    ''' 
    class will read a file looking for a duplicate key and then add a count field to the end to state the number of duplicates found 
    
    steps:  
    1 - sort the file by the passed in key
    2 - read sequentially, loading the previous record into a list.
    3 -  once the key doesn't match write each record from the list out with the new field count equal to the length of the list
    
    '''
    
    def execute_processor(self):
        ''' parameters needed, file name, key (comma seperated list) '''
        
        file_in = self.param_dict['file_in']
        new_name = self.param_dict['count_name']
        keys = self.param_dict['key'].split(",")
        
        full_path = os.path.join(self.entry.working_directory,file_in)
        
        self.sort_one_file(full_path, keys)
        rec_list = []
        
        prev_rec = None
        
        
        with open(full_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                vals = [row[a] for a in keys]
                key = "_".join(vals)
                
                if prev_rec and prev_rec != key:
                    self.write_recs(rec_list,new_name)
                    rec_list = []
                    prev_rec = key
                elif not prev_rec:
                    header = row.keys()
                    header.append(new_name)
                    self.setup_csv_temp_writer(self.get_temp_csv_name(), header, write_header=True)
                    prev_rec = key
                
                
                rec_list.append(row)
        self.write_recs(rec_list,new_name)
        
        self.close_temp_csv()   
        return 0
            
    def write_recs(self, rec_list, name):
        for rec in rec_list:
            rec[name] = len(rec_list)
            self.write_temp_rec(rec)
                            
                
    def sort_one_file(self, csv_in, columns):
       
        has_header = True
        max_size = int(self.param_dict.get('max_size','100'))
        delimiter = self.param_dict.get('delimiter',',')
        
        columns = [int(column) if column.isdigit() else column for column in columns]
        
        
        global TMP_DIR 
        TMP_DIR = os.path.join(self.entry.working_directory,'.csvsort.%d' % os.getpid())

        csvsort(csv_in, columns, None, max_size, has_header, delimiter)
        
        

class call_main_python(BaseProcessor):
    ''' 
    call the main module of a python class
    can add as many arguments as needed 
    
    put the arguments in order with the key being arg1, arg2, arg3, ...
    
    arg1 = in argument
    arg2 = 2nd argument
    ...
    
    '''
    
    def execute_processor(self):
        python_class = self.param_dict['python_class']
        arg_list = []
        
        for x in range(len(self.param_dict.keys())):
            key = "arg" + str(x + 1)
            value = self.param_dict.get(key,None)
            if value:
                arg_list.append(value)  
        
        ''' code here is to ensure arguments with spaces will work as intended (in a pythonic way)'''          
        new_list = ['"'+arg+'"' if (' ' in arg) else arg for arg in arg_list]
        '''       add " around it   check for space          iterate the list ''' 
          
        ret_value = 0
        try:
            os.system('python '+python_class+' %s' % ' '.join(new_list))
        
        except Exception:
            print "ERROR ERROR - There was a problem in the execution of python class: "+python_class
            ret_value = 1
        
        return ret_value
        
        
    
class copy_file(BaseProcessor):
    ''' copy a file to a new location 
        defaults to the old name unless a new one 
        is supplied as a parameter
        '''
    def execute_processor(self):
        filename = self.param_dict['copy_file']
        destination = self.param_dict['destination']
        new_name = self.param_dict.get('new_name',filename)
        
        full_path = os.path.join(self.entry.working_directory,filename)
        new_path = os.path.join(destination,new_name)
        
        shutil.copy(full_path, new_path)
        
        return 0

class add_max_min_date(BaseProcessor):
    ''' sometimes for reporting purposes it is helpful to know how much difference there is between the record date and the min and max 
    and some tools are better at doing that for you than others... so this will help if the tool you are using doesn't '''
    
    def execute_processor(self):
        filename = self.param_dict['in_file']
        date_field = self.param_dict['date_field']
        
        max_field = "max_"+date_field
        min_field = "min_"+date_field
        
        csv_in = os.path.join(self.entry.working_directory,filename)
        
        max_d, min_d, header = self.get_min_max(csv_in, date_field)
        
        with open(csv_in) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not header:
                    header = row.keys()
                    header.append(max_field)
                    header.append(min_field)
                rec_date_str = row[date_field]
                
                rec_date = RawDataUtilities.date_from_string(rec_date_str)
                
                if not max_d:
                    max_d = rec_date
                
                adelta = max_d - rec_date
                
                if adelta < datetime.timedelta(minutes=1):
                    max_d = rec_date
                
                if not min_d:
                    min_d = rec_date
                    
                adelta = rec_date - min_d

                if adelta < datetime.timedelta(minutes=1):
                    min_d = rec_date
        
        self.setup_csv_temp_writer(self.get_temp_csv_name(), header, write_header=True)
        
        with open(csv_in) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                out_dict = {}
                out_dict[max_field] = max_d
                out_dict[min_field] = min_d
                for key in row.keys():
                    out_dict[key] = row[key]
                self.write_temp_rec(out_dict)
                
        self.close_temp_csv()
        
        return 0
    
    def get_min_max(self,csv_in, date_field):
        max_field = "max_"+date_field
        min_field = "min_"+date_field
        max_d = None
        min_d = None
        header = []
        with open(csv_in) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if not header:
                    header = row.keys()
                    header.append(max_field)
                    header.append(min_field)
                rec_date_str = row[date_field]
                
                rec_date = RawDataUtilities.date_from_string(rec_date_str)
                
                if not max_d:
                    max_d = rec_date
                
                adelta = max_d - rec_date
                
                if adelta < datetime.timedelta(minutes=1):
                    max_d = rec_date
                
                if not min_d:
                    min_d = rec_date
                    
                adelta = rec_date - min_d

                if adelta < datetime.timedelta(minutes=1):
                    min_d = rec_date
        return max_d, min_d, header
    
if __name__ == "__main__":
    """
    allow to run outside of framework
    """
    params = {}
    params['run_date'] = datetime.datetime.today()
    params['name'] = 'merge_adp_sup1'
    params['source_file'] = None
    params['temp_results'] = 'None'
    params['description'] = "Move a file from 1 location to another"
    params['src_implementation'] = ""
    params['working_directory'] = r'D:\python_scripts\rawdataprocessor\output'
    params['in_file'] = 'merge_adp_sup.csv'
    params['date_field'] = 's_end_date'
    params['instantiate'] = "false"
    
    c_entry = ConfigEntry(params)
    params['entry'] = c_entry
    sups = add_max_min_date(params)
    sups.execute_processor()