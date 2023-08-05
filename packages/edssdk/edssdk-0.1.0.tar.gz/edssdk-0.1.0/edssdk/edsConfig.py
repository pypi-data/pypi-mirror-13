#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: edsConfig.py
# Author: xingming
# Mail: huoxm@zetyun.com 
# Created Time:  2016-01-06 17时56分14秒
#############################################

class ehcConfig:
    def __init__(self, conf=None):
        self.ehc_id = None
        self.ehc_name = None
        self.description = None
        self.vpc_id = None
        self.ehc_status = None
        
        self.user_id = None
        
        self.cloud_password = None
        self.cloud_type = None
        self.cloud_region = None
        self.cloud_zone = None
        self.cloud_cidr = None
        self.cloud_dsize = 100
        
        self.cluster_type = None
        self.master_type = None
        self.slave_type = None
        self.slave_num = 0
        
        self.command_id = None
        self.command_name = None
        self.command_description = None
        self.command_type = None
        self.command_conf = None
        

