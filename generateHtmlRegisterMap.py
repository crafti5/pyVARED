import os
from templateFileGeneration import *

class GenerateHTMLMap(TemplateGeneration):
    
    FILE_ENDING = '.html'
    BIT_DEFINE_STRING = '<tr><td align="middle">Bit{0}</td><td align="middle">{1}</td><td align="middle"><span title="{3}" class="tooltip">{2}</span></td></tr>'
    CSS_STYLE_SETUP = '''<style type="text/css">
                        h1{background-color:#d9d9d9;font-family: Arial, Helvetica, sans-serif;text-shadow: 1px 1px 0px #fff;} 
                        table{font-family:Arial, Helvetica, sans-serif;color:#666;font-size:12px;text-shadow: 1px 1px 0px #fff;background:#eaebec;margin:20px;border:#ccc 1px solid;-moz-border-radius:3px;-webkit-border-radius:3px;border-radius:3px;-moz-box-shadow: 0 1px 2px #d1d1d1;-webkit-box-shadow: 0 1px 2px #d1d1d1;box-shadow: 0 1px 2px #d1d1d1;}
                        td {width: 600px;} 
                        ht {padding:21px 25px 22px 25px;border-top:1px solid #fafafa;border-bottom:1px solid #e0e0e0;background: #ededed;background: -webkit-gradient(linear, left top, left bottom, from(#ededed), to(#ebebeb));background: -moz-linear-gradient(top,  #ededed,  #ebebeb);}
                        table th:first-child {text-align: left;padding-left:20px;}
                        table tr:first-child th:first-child {-moz-border-radius-topleft:3px;-webkit-border-top-left-radius:3px;border-top-left-radius:3px;}
                        table tr:first-child th:last-child {-moz-border-radius-topright:3px;-webkit-border-top-right-radius:3px;border-top-right-radius:3px;}
                        table tr {text-align: center;padding-left:20px;}
                        table td:first-child {text-align: left;padding-left:20px;border-left: 0;}
                        table td {padding:18px;border-top: 1px solid #ffffff;border-bottom:1px solid #e0e0e0;border-left: 1px solid #e0e0e0;background: #fafafa;background: -webkit-gradient(linear, left top, left bottom, from(#fbfbfb), to(#fafafa));background: -moz-linear-gradient(top,  #fbfbfb,  #fafafa);}
                        table tr.even td {background: #f6f6f6;background: -webkit-gradient(linear, left top, left bottom, from(#f8f8f8), to(#f6f6f6));background: -moz-linear-gradient(top,  #f8f8f8,  #f6f6f6);}
                        table tr:last-child td {border-bottom:0;}
                        table tr:last-child td:first-child {-moz-border-radius-bottomleft:3px;-webkit-border-bottom-left-radius:3px;border-bottom-left-radius:3px;}
                        table tr:last-child td:last-child {-moz-border-radius-bottomright:3px;-webkit-border-bottom-right-radius:3px;border-bottom-right-radius:3px;}
                        table tr:hover td {background: #f2f2f2;background: -webkit-gradient(linear, left top, left bottom, from(#f2f2f2), to(#f0f0f0));background: -moz-linear-gradient(top,  #f2f2f2,  #f0f0f0);}
                        .tooltip{display: inline;position: relative; white-space:pre-line;text-shadow: 0px 0px 0px #fff}
                        .tooltip:hover:after{background: #333;background: rgba(0,0,0,.8);border-radius: 5px; bottom: 26px;color: #fff;content: attr(title);left: 20%;padding: 5px 15px;position: absolute;z-index: 98;width: 220px;}
                        .tooltip:hover:before{white-space:pre-wrap;border: solid;border-color: #333 transparent;border-width: 6px 6px 0 6px;bottom: 20px;content: "";left: 50%;position: absolute;z-index: 99;}</style>'''
    
    GENERAL_REGISTER_DEFINITION = '''<table border=1 frame=hsides rules=rows><tr><td align="middle" style="font-size:20px"><b>Register Name</b></td>
                                    <td align="middle" style="font-size:20px"><b>Component Register Offset</b></td><td align="middle" style="font-size:20px">
                                    <b>Read-Write-Option</b></td></tr><tr><td align="middle" style="background-color:#58FAF4" id="{0}">{0}</td>
                                    <td align="middle" style="background-color:#58FAF4">{1}</td><td align="middle" style="background-color:#58FAF4">{2}</td></tr>'''
    REGISTER_BIT_INFORMATION = '{0}</table>'
    AUTOGENERATION_HINT = '<!-- This file is automatically generated, don''t modify it! -->\n'
    
    def _extract_bit_defintion(self, key_value_pair):
        ''' extract the bits for a register and calculate / generate the bits '''
        return_string = ''
        key_value_pair = sorted(key_value_pair, key=self._get_key)
        shift_value = ''
        bit_mask_value = 0
        for name, value in key_value_pair:
            if(len(value[0])>1 and isinstance(value[0], list)):
                bit_value_list = [int(i) for i in value[0]]
                bit_list = range(max(bit_value_list), min(bit_value_list)-1, -1)
                shift_value += '|'.join('1<<{0} '.format(n) for n in bit_list)
                bit_mask_value = sum(2**n for n in bit_list)
            else:
                shift_value = '1<<' + str(value[0])
                bit_mask_value = 2**int(value[0])
            return_string += self.BIT_DEFINE_STRING.format(value[0], name, shift_value, self._format_mask_value(bit_mask_value))
        return return_string

    def _format_mask_value(self, bit_mask_value):
        ''' calculate the mask value in different views like binary, decimal and hexadecimal. This will used at tooltip in browser'''
        return 'Decimal: {0}\nHexidecimal: {1}\nBinary: {2}'.format(bit_mask_value, hex(bit_mask_value), bin(bit_mask_value)[2:])
        
    def _extract_register_information(self):
        ''' extraction of the slave register and all including bits '''
        return_string = ''
        keylist = self.parsed_file.register.keys()
        keylist.sort()
        for temp_reg in keylist:
            return_string += self.GENERAL_REGISTER_DEFINITION.format(self._extract_variable_name(temp_reg), 
                                                                     self._calculate_register_offset(self.parsed_file.register[temp_reg].binary_coded[2:]), 
                                                                     self._extract_read_write_option(self.parsed_file.register[temp_reg].option))
            return_string += self.REGISTER_BIT_INFORMATION.format(self._extract_bit_defintion(self.parsed_file.register[temp_reg].bit_definition))
        return return_string
        
    def _write(self):
        ''' write the whole file '''
        self.output_file.write(self.AUTOGENERATION_HINT)
        out_string = self._extract_register_information()
        self.output_file.write('<!doctype html><html><body><head>{0}<h1 align="middle" id="{1}">{1} (Version: {2})</h1></head>\n{3}</body>'.format(self.CSS_STYLE_SETUP, 
                                                                                                                                                   self.parsed_file.component_name, 
                                                                                                                                                   self._extract_date_information(self.parsed_file.ip_core_version), 
                                                                                                                                                   out_string))
        
class GenerateComponentIndex(GenerateHTMLMap):
    
    BASIC_HTML_TEMPLATE = '<!DOCTYPE html><h1>Component Index</h1><ul>{0}</ul><html><body>{1}'
    FILE_ENDING = '.html'
    
    def __init__(self, component_name, output_file_name):
        self.component_names = component_name
        with open(output_file_name.format('.html'), 'rb') as read_file:
            self.read_hardware_file = read_file.read()
            read_file.close()
        os.remove(output_file_name.format('.html'))
        self.output_file = open(output_file_name.format(self.FILE_ENDING), 'a')
        self._write()
    
    def _extract_variable_name(self, temp_reg):
        ''' extract the register name if it has an alias. If it doesn't have a alias it will be called as original name generated in VHDL '''
        if(temp_reg.variable_name != None):
            return temp_reg.variable_name
        else:
            return temp_reg.orginal_slave_name
        
    def _extract_offsets_names(self, register):
        ''' extract the register offset for all register found in file'''
        offset_dict = dict()
        for temp_reg in register.keys():
            offset_dict[int(self._calculate_register_offset(register[temp_reg].binary_coded[2:]), 16)] = self._extract_variable_name(register[temp_reg])
        return offset_dict
        
    def _extract_register_name(self, register):
        ''' extraction of the slave register '''
        return_string = ''
        offset_list = self._extract_offsets_names(register)
        keylist = offset_list.keys()
        keylist.sort()
        for temp_reg in keylist:
            return_string += '<li style="margin-left:50px;font-family: Arial, Helvetica, sans-serif;font-size:12px"><a href="#{0}">{1} - {0}</a></li>'.format(offset_list[temp_reg], hex(temp_reg))
        return return_string

    def _write_index(self): 
        ''' write the component register with some formatting for html '''
        result_string = ''
        for temp_component, temp_version, temp_register in self.component_names:
            result_string += '''<details><summary style="margin-bottom: 10px;margin-top: 20px;font-family: Arial, Helvetica, sans-serif;"><a href="#{0}">
                                <div style="display:inline-block;font-weight: bold;">{0}</div></a><div style="font-size:14px;">
                                (Version: {1})</div></summary>{2}</details>'''.format(temp_component, self._extract_date_information(temp_version), self._extract_register_name(temp_register))
        return result_string
    
    def _write(self):
        ''' write the whole file '''
        self.output_file.write(self.BASIC_HTML_TEMPLATE.format(self._write_index(), self.read_hardware_file))