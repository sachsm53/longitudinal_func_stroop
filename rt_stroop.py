#!/usr/bin/python

import os
import sys
import csv
import pandas as pd
import numpy as np

reload(sys)
sys.setdefaultencoding('utf8')


datafolder = "/Volumes/MusicProject/Longitudinal_study/Functional/log_stroop/"

#logging colors
sectionColor = "\033[94m"
sectionColor2 = "\033[96m"
groupColor = "\033[90m"
mainColor = "\033[92m"
pink = '\033[95m'
yellow = '\033[93m'
red = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

waves = ["groupA_Y3", "groupB_Y3"]
#waves = ["groupA_Y3"]

for wave in waves: 
	print pink + '%s%s\n' %(wave,mainColor)
	groupList = ['Control', 'Music', 'Sport']


	for group in groupList:
		subjectDir = datafolder + "%s/%s/" %(wave,group)
		subjectList = [elem for elem in os.listdir(subjectDir) if "." not in elem] 
		excludeList = ['C19','S108','C07','C111','M02','S07','S14','S28','M109']
		subjectList = [elem for elem in subjectList if elem not in excludeList]
		#subjectList = ['C01']
		print subjectList


		for subj in subjectList:
			subject = subj
			subjfolder = subjectDir + subject + "/"

			logfiles = [elem for elem in os.listdir(subjfolder) if ".DS" not in elem] 
			run = 0
			

			for log in logfiles:
				run = run + 1
				#print yellow + '%s\t%d%s' %(subject,run,mainColor)
				logfile = subjfolder + log
				i_nacount = 0
				c_nacount = 0

				df = pd.read_csv(logfile, sep = '\t', parse_dates = True, header = None, names = ["onset","colorword","colorink","reaction","reaction2"], skip_blank_lines = True) 
				
				con1_s = df.onset[0:12]
				incon1_s = df.onset[12:24]
				con2_s = df.onset[24:36]
				incon2_s = df.onset[36:48]
				con3_s = df.onset[48:60]
				incon3_s = df.onset[60:72]
 
				con1_e = df.reaction[0:12]
				incon1_e = df.reaction[12:24]
				con2_e = df.reaction[24:36]
				incon2_e = df.reaction[36:48]
				con3_e = df.reaction[48:60]
				incon3_e = df.reaction[60:71]

				c1_rt = con1_e - con1_s
				c2_rt = con2_e - con2_s
				c3_rt = con3_e - con3_s
				i1_rt = incon1_e - incon1_s
				i2_rt = incon2_e - incon2_s
				i3_rt = incon3_e - incon3_s

				c1 = list(c1_rt)
				c2 = list(c2_rt)
				c3 = list(c3_rt)
				i1 = list(i1_rt)
				i2 = list(i2_rt)
				i3 = list(i3_rt)

				# #Count the number of NAs for each trial
				# for i in range(0,len(c1_rt)): 
				# 	#print c1_rt[i]
				# 	if np.isnan(c1[i]) == True or np.isnan(c2[i]) == True or np.isnan(c3[i]) == True:
				# 		#print "Found some Nas in the congruent"
				# 		c_nacount = c_nacount + 1
				# 	elif np.isnan(i1[i]) == True or np.isnan(i2[i]) == True or np.isnan(i3[i]) == True:
				# 		#print "Found some Nas in the incongruent"
				# 		i_nacount = i_nacount + 1
				# print red + '%s\t%d\t%d\t%d%s' %(subject,run,c_nacount,i_nacount,mainColor)


				#Remove any response time that is an outlier (more or less than 2 standard deviations above the mean)
				c_rt = c1 + c2 + c3
				i_rt = i1 + i2 + i3
				c_std = np.nanstd(c_rt)
				i_std = np.nanstd(i_rt)
				upper = np.mean(c_rt) + (2*c_std)
				lower = np.mean(c_rt) - (2*c_std)
				upper2 = np.mean(i_rt) + (2*i_std)
				lower2 = np.mean(i_rt) - (2*i_std)

				for i in range(0,len(c_rt)): 
					if c_rt[i] > upper or c_rt[i] < lower:
						#print "This CONGRUENT trial %d in %s run %d is an outlier" %(i,subject,run)
						#print upper, lower
						c_rt[i] = np.nan
						#del i_rt[i]
						#np.delete(c1,i)

				for i in range(0,len(i_rt)): 
					if i_rt[i] > upper2 or i_rt[i] < lower2:
						#print "This INCONGRUENT trial %d in %s run %d is an outlier" %(i,subject,run)
						#print upper2, lower2
						i_rt[i] = np.nan
						#del i_rt[i]
						#np.delete(c1,i)
				c_rt_mean = np.nanmean(c_rt)
				i_rt_mean = np.nanmean(i_rt)
				print red + '%s\t%d\t%f\t%f%s' %(subject,run,c_rt_mean,i_rt_mean,mainColor)
					# elif np.isnan(i1[i]) == True or np.isnan(i2[i]) == True or np.isnan(i3[i]) == True:
					# 	#print "Found some Nas in the incongruent"
					# 	i_nacount = i_nacount + 1



				print red + '%s\t%d\t%d\t%d%s' %(subject,run,c_nacount,i_nacount,mainColor)


				c1_mean_rt = c1_rt.mean()
				c2_mean_rt = c2_rt.mean()
				c3_mean_rt = c3_rt.mean()
				i1_mean_rt = i1_rt.mean()
				i2_mean_rt = i2_rt.mean()
				i3_mean_rt = i3_rt.mean()



				# if math.isnan(con1_e) == True:
				# 	#print "no second button press"
				# 	con1_e = df.reaction[11]
				# 	if math.isnan(con1_e) == True: 
				# 		con1_e = df.onset[11] + 1.7

				# incon1_e = df.reaction2[11+12]
				# if math.isnan(incon1_e) == True:
				# 	#print "no second button press"
				# 	incon1_e = df.reaction[11+12]
				# 	if math.isnan(incon1_e) == True: 
				# 		incon1_e = df.onset[11+12] + 1.7

				# con2_e = df.reaction2[11+12+12]
				# if math.isnan(con2_e) == True:
				# 	#print "no second button press"
				# 	con2_e = df.reaction[11+12+12]
				# 	if math.isnan(con2_e) == True: 
				# 		con2_e = df.onset[11+12+12] + 1.7

				# incon2_e = df.reaction2[11+12+12+12]
				# if math.isnan(incon2_e) == True:
				# 	#print "no second button press"
				# 	incon2_e = df.reaction[11+12+12+12]
				# 	if math.isnan(incon2_e) == True: 
				# 		incon2_e = df.onset[11+12+12+12] + 1.7

				# con3_e = df.reaction2[11+12+12+12+12]
				# if math.isnan(con3_e) == True:
				# 	#print "no second button press"
				# 	con3_e = df.reaction[11+12+12+12+12]
				# 	if math.isnan(con3_e) == True: 
				# 		con3_e = df.onset[11+12+12+12+12] + 1.7

				# incon3_e = df.reaction2[11+12+12+12+12+12]
				# if math.isnan(incon3_e) == True:
				# 	#print "no second button press"
				# 	incon3_e = df.reaction[11+12+12+12+12+12]
				# 	if math.isnan(incon3_e) == True: 
				# 		incon3_e = df.onset[11+12+12+12+12+12] + 1.7

				# c1l = con1_e - con1_s
				# c2l = con2_e - con2_s
				# c3l = con3_e - con3_s

				# ic1l = incon1_e - incon1_s
				# ic2l = incon2_e - incon2_s
				# ic3l = incon3_e - incon3_s

				# if c1l or c2l or c3l or ic1l or ic2l or ic3l < 22:
				# 	print red + "Found a trial where the block lenth is unusual short: %s, run %d%s" %(subj,run,mainColor)

				# cong_mat = np.array([ [con1_s,c1l,1], [con2_s,c2l,1], [con3_s,c3l,1] ])
				# print cong_mat
				# print
				# np.savetxt(cong_evfile, cong_mat, fmt = '%1.5f', delimiter='\t')

				# incong_mat = np.array([ [incon1_s,ic1l,1], [incon2_s,ic2l,1], [incon3_s,ic3l,1] ])
				# print incong_mat
				# print
				# np.savetxt(incong_evfile, incong_mat, fmt = '%1.5f', delimiter='\t')

