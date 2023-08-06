# -*- coding: utf-8 -*-
import datetime

class ExperimentWarning:
    
    def __init__(self, name, varname, killvalue, comparator, when, action):
        self.name = name.strip()
        self.varname = varname.strip()
        self.killvalue = killvalue
        self.comparator = comparator.strip()
        self.when = when.strip()
        self.action = action.strip()
        self.start_time = datetime.datetime.now()
        
    def get_action(self, logrow):
        logrow = logrow.strip()
        varlen = len(self.varname)
        check_condition = True
        if 'time' in self.when:
            time_when = float(self.when[4:].strip())
            time_passed = datetime.datetime.now() - self.start_time
            time_passed_sec = time_passed.days * 86400 + time_passed.seconds
            time_passed_min = time_passed_sec / 60
            if time_passed_min < time_when:
                check_condition = False
        if check_condition and logrow[:varlen].strip() == self.varname:
            varvalue = logrow[varlen:].strip()
            try:
                varvalue = float(varvalue)
            except:
                return 'no action'
            if any( [self.comparator == 'gt' and varvalue > self.killvalue,
                self.comparator == 'lt' and varvalue < self.killvalue,
                self.comparator == 'eq' and varvalue == self.killvalue,
                self.comparator == 'geq' and varvalue >= self.killvalue,
                self.comparator == 'leq' and varvalue <= self.killvalue] ):
                return self.action
        return 'no action'
            
