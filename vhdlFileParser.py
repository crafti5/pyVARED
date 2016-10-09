from registerDefinition import *

REGISTER_SIZE = 32

class FileParseOperation():
    
    def __init__(self, path):
        self.file_path = path
        self.variable_definition = False
        self.process = False
        self.read_process = False
        self.write_process = False
        self.ip_core_version = None
        self.ip_core_version_naming = None
        self.register = {}
        self.component_name = self._extract_component_name()
        self._parse_file_for_slave_register()

    def _extract_component_name(self):
        # to separate the component we need the "/" and also the "_v"
        return self.file_path[self.file_path.rfind('/')+1:self.file_path.rfind('_v')].upper()

    def _extract_bit_definition(self, line):
        if('signal slv_reg' in line and 'signal slv_reg_' not in line):
            ############## extract the slave register name and get rid of unnecessary symbols ##############
            slave_name = line[line.find('slv'):line.find(':')].replace(' ', '').replace('\t', '')
            self.register[slave_name] = RegisterDefinition()
            self.register[slave_name].component_name = self.component_name
            self.register[slave_name].orginal_slave_name = slave_name
            self.register[slave_name].binary_coded = bin(int(slave_name[slave_name.find('g')+1:]))
        elif('alias' in line and 'slv_reg' in line):
            ############## extract big definition here ##############
            temp_reg_name = line[line.find('slv_'):line.rfind('(')]
            alias_search_string = 'alias a_'
            alias_name = line[line.find(alias_search_string)+len(alias_search_string):line.find(':')].replace(' ', '')
            bit_depth = line[line.rfind('(')+1:line.rfind(')')].replace(' ', '')
            try:
                if('downto' in bit_depth):
                    bit_depth = [int(bit_depth[:bit_depth.find('do')]), int(bit_depth[bit_depth.rfind('to') + 2:])]
                    if((bit_depth[0]-bit_depth[1]) == REGISTER_SIZE-1):
                        self.register[temp_reg_name].variable_name = alias_name.upper()
                        if('control' in alias_name):
                            self.register[temp_reg_name].option['write'] = True
                            self.register[temp_reg_name].option['finished'] = True
                        elif('status' in alias_name):
                            self.register[temp_reg_name].option['read'] = True
                            self.register[temp_reg_name].option['finished'] = True
                    elif((bit_depth[0]-bit_depth[1]) < REGISTER_SIZE-1):
                        self.register[temp_reg_name]._add_bit_definition(alias_name, [bit_depth, ])
                elif('to' in bit_depth):
                    pass
                else:
                    self.register[temp_reg_name]._add_bit_definition(alias_name, [bit_depth, ])
            except Exception as e:
                print(alias_name)
                print('Cannot convert bit_depth "{0}" type: "{1}"\n{2}'.format(bit_depth, type(bit_depth), str(e)))

    def _check_address_and_register_binary(self, line):
        if('when b"' in line):
            temp_binary_address = bin(int(line[line.find('"')+1: line.rfind('"')], 2))
            for temp_reg in self.register.keys():
                if(self.register[temp_reg].binary_coded == temp_binary_address):
                    return (temp_reg, True)
            return (None, False, int(line[line.find('"')+1: line.rfind('"')], 2))
        
    def _parse_file_for_slave_register(self):
        self.version_check = False
        self.temp_register_name = None
        for line in open(self.file_path, 'rb').readlines():
            ############## extract variable definition here ##############
            if('architecture' in line):
                self.variable_definition = True
            if(self.variable_definition):
                self._extract_bit_definition(line)
            if('constant' in line and '_VERSION' in line):
                # we need the name for further mapping of the slv reg and also the version definition 
                self.ip_core_version_naming = line[line.find('constant ')+9:line.find('SION')+4]
                self.ip_core_version = line[line.find('x"')+2:line.rfind('";')]
            ############## read and write access must be defined ##############
            if('begin' in line):
                self.variable_definition = False
            if('process(S_AXI_ACLK)' in line.replace(' ', '')):
                self.process = True
            elif('process' in line and 'slv_reg_rden' in line and 'S_AXI_ARESETN' in line):
                self.read_process = True
                self.write_process = False
                self.process = False
            if(self.process):
                if('case loc_addr is' in line):
                    self.write_process = True
            if(self.read_process):
                boolean_read = self._check_address_and_register_binary(line)
                if(self.version_check):
                    if(self.ip_core_version_naming != None and self.ip_core_version_naming in line):
                        temp_slv_name = 'slv_reg{0}'.format(self.temp_register_name)
                        self.register[temp_slv_name] = RegisterDefinition()
                        self.register[temp_slv_name].component_name = self.component_name
                        self.register[temp_slv_name].orginal_slave_name = self.ip_core_version_naming
                        self.register[temp_slv_name].binary_coded = bin(self.temp_register_name)
                    self.version_check = False
                if(boolean_read == None): continue
                elif(len(boolean_read) > 2):
                    self.version_check = True
                    self.temp_register_name = boolean_read[2]
                elif(boolean_read[1]):
                    self.register[boolean_read[0]].option['read'] = True
            if(self.write_process):
                boolean_write = self._check_address_and_register_binary(line)
                if(boolean_write == None): continue
                elif(boolean_write[1]):
                    self.register[boolean_write[0]].option['write'] = True
            if('end process' in line):
                self.process = False
                self.read_process = False
                self.write_process = False
                self.version_check = False
        
        ############## set the attributes of the enumeration ##############
        for temp_register_map in self.register.keys():
            self.register[temp_register_map].ip_core_version = self.ip_core_version
