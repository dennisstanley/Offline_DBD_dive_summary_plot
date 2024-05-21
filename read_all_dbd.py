
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
takes all the DBD files in the present directory
plots them and saves the plot under glider id directory
then moves the processed DBD into a subdirectory of
glider id directory 

'''


import numpy as np  #stand on giants shoulders
import pandas as pd
import matplotlib.pyplot as plt
import os
import platform
import linecache



EBD_Read=False
file="08500000.DBD"  # the comand line version will take this as an argument
EBDfile=file[:-3]+"EBD"
txtfile="DBD_temp.txt"
EBDtxtfile="EBD_temp.txt"

DirectoryContents=os.listdir()
OperatingSystem=platform.system()
print("detected operating system is "+OperatingSystem)
print()
print("I found the following dbd files to process")
for filename in DirectoryContents:
    if filename.endswith("dbd") or filename.endswith("DBD"):
        print (filename)


for filename in DirectoryContents:
    if (filename.endswith("dbd")+filename.endswith("DBD")): #go through the list of directory contents untll you find a .dbd or .DBD
        print ("processing  " +filename)
        file=filename


        if OperatingSystem=="Linux":
            #linux: process dbd and store as temp txt file
            #The webb linux executable dbd2asc must be in the PWD
            #the excutable processes the DBD to text at STDOUT this is piped to a text file 
            
            
            os.system("./dbd2ascNEW "+file+" > "+txtfile) 
            if EBD_Read:
                os.system("./dbd2asc "+EBDfile+" > "+EBDtxtfile) 
        elif OperatingSystem=="Windows":   
        
            #Windows: process dbd and store as temp txt file
            #The webb linux executable dbd2asc must be in the PWD
            #the excutable processes the DBD to text at STDOUT this is piped to a text file 
            
            
            os.system("dbd2asc.exe "+file+" > "+txtfile)
            if EBD_Read:
                os.system("dbd2asc.exe "+EBDfile+" > "+EBDtxtfile)
        else:
            print('operating system not supported Only Windows or Linux')
        #import data from text file into python
        
        linecache.clearcache() 
        #load_metadata_incluing column names
        mission_name = linecache.getline(txtfile, 9)[14:-4]  # get row 9 but ignore the first 14 and last 4 characters 
        num_ascii_tags=  int(linecache.getline(txtfile, 3)[16:]) # this is length of metadat record
        unit_id=linecache.getline(txtfile, 5)[10:]
        
        #locate data in file ie after the metadata
        title_row=num_ascii_tags
        Units_row=num_ascii_tags+1
        first_data_row=num_ascii_tags+2
        
        
        header_row = pd.read_csv(txtfile, skiprows=title_row, nrows=1, delimiter=' ', header=None)
        Units = pd.read_csv(txtfile, skiprows=Units_row, nrows=1, delimiter=' ', header=None)
        dbd_data_initial_values = pd.read_csv(txtfile, skiprows=first_data_row, nrows=1 , delimiter=' ', header=None)
        
        
        
        #load the actula data then apply column names to the data, units and initial values
        dbd_data = pd.read_csv(txtfile, skiprows=first_data_row+1, delimiter=' ', header=None)
        dbd_data.columns = header_row.values[:][0]
        Units.columns = header_row.values[:][0]
        dbd_data_initial_values.columns = header_row.values[:][0]
        
        #set up the plots 
        fig = plt.figure(figsize=(14,20))
        fig.suptitle(mission_name +' '+unit_id, fontsize=16)
        
        #Make output directory (unit number)of it doesn't already exist '
        
        if not os.path.exists(os.getcwd() + '/' + unit_id[0:7]):
            os.makedirs(os.getcwd() + '/' + unit_id[0:7], exist_ok=True) 
        if not os.path.exists(os.getcwd() + '/' + unit_id[0:7]+"/processed_files"):
            os.makedirs(os.getcwd() + '/' + unit_id[0:7]+"/processed_files", exist_ok=True)
        
        axdepth = fig.add_subplot(421)
        axballast = axdepth.twinx() 
        axaltim=axdepth.twinx()
        #more than one twinax with offset axises axai ?? https://stackoverflow.com/questions/48618992/matplotlib-graph-with-more-than-2-y-axes
        axdepth.set_title('Depth')
        axdepth.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_depth'], marker='o', markersize=4,label="depth")
        axballast.plot(dbd_data["m_present_secs_into_mission"], dbd_data['c_ballast_pumped'],color= "green",label="c_ballast")
        axballast.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_ballast_pumped'],color= "orange",label="m_ballast")
        axballast.spines["right"].set_position(("axes", 1.05))
        axaltim.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_raw_altitude'], marker='o',color= "black", markersize=4,label="altim height")
        
        axdepth.set_ylim(axdepth.get_ylim()[::-1]) #reverse the y axis https://stackoverflow.com/questions/2051744/reverse-y-axis-in-pyplot
        axdepth.legend(loc=6) # legend locations https://matplotlib.org/2.0.1/api/_as_gen/matplotlib.axes.Axes.legend.html
        axballast.legend(loc=7)
        axaltim.legend(loc=4)
        axdepth.grid()
        
        
        
        axpitch = fig.add_subplot(423)
        axbattpos = axpitch.twinx() 
        axpitch.set_title('Pitch')
        axpitch.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_pitch']*57.3,color='blue',label="m_pitch Deg")
        
        axpitch.plot(dbd_data["m_present_secs_into_mission"][::2], dbd_data['m_pitch'][::2]*0-26, marker= 'o',color='blue',markersize=1,alpha=0.4,linestyle = 'None',label="+- 26deg (nominal)")
        axpitch.legend(loc=2)
        axpitch.plot(dbd_data["m_present_secs_into_mission"][::2], dbd_data['m_pitch'][::2]*0+26, marker= 'o',color='blue',markersize=1,alpha=0.4,linestyle = 'None')
        
        axbattpos.plot(dbd_data["m_present_secs_into_mission"], dbd_data['c_battpos'],color= "green",label="c_battpos")
        axbattpos.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_battpos'],color= "orange",label="m_battpos")
        axbattpos.legend(loc=1)
        axpitch.set_ylim(-60,60) 
        axbattpos.set_ylim(1.5,-1.5) 
        axpitch.grid()
        
        
        axroll = fig.add_subplot(422)
        axfin = axroll.twinx() 
        axroll.set_title('Roll')
        axroll.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_roll']*57.3,label="roll")
        axfin.plot(dbd_data["m_present_secs_into_mission"], dbd_data['c_fin']*57.3,color= "green",label="c_fin")
        axfin.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_fin']*57.3,color= "orange",label='m_fin')
        axroll.set_ylim(-15,15)
        axfin.set_ylim(-15,15)  
        axroll.legend(loc=2)
        axfin.legend(loc=1)
        axroll.grid()
        
        
        axheading= fig.add_subplot(424)
        axheading.set_title('Heading')
        axheading.plot(dbd_data["m_present_secs_into_mission"], dbd_data['m_heading']*57.3,label="m_heading")
        axheading.plot(dbd_data["m_present_secs_into_mission"], dbd_data['c_heading']*57.3,label="c_heading")
        axheading.legend(loc=1)
        
        
        axpath = fig.add_subplot(224)
        axpath.set_title('path Local Mission Coordinates (m)')
        axpath.plot(dbd_data["m_x_lmc"], dbd_data['m_y_lmc'], marker='o', markersize=4)
        axpath.text(0,0, "start")
        axpath.text(dbd_data["m_x_lmc"][-1:], dbd_data['m_y_lmc'][-1:], "finish")
        
        axpath.grid()
        
        
        #plt.savefig(unit_id[0:7]+"/"+ unit_id +'_'+ mission_name+".png",format="png")
        plt.savefig(unit_id[0:7]+"/"+unit_id[:-1] +'_'+ mission_name+".png",format="png")
        plt.show()
        
        #  move processed files out of working directory to "processed files" directory
        print ("archiving "+filename  ) 
        if OperatingSystem=="Linux":
            os.system("mv "+file[:-3]+"* "+os.getcwd() + '/' + unit_id[0:7]+"/processed_files")
            
        elif OperatingSystem=="Windows":   
            # windows move processed files out of working directory to "processed files" directory
            os.system("move "+file[:-3]+"* "+os.getcwd() + '/' + unit_id[0:7]+"/processed_files")
           
print("finished") 
print("process binary files were archived to processed directory under relevent glider subdirectory")   


