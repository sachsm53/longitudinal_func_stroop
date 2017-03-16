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
		excludeList = ['C19','S108']
		subjectList = [elem for elem in subjectList if elem not in excludeList]
		#subjectList = ['C01']
		print subjectList


		for subj in subjectList:
			subject = subj
			subjfolder = subjectDir + subject + "/"
			checkfile = subjfolder + "ev_incong_run2.txt"

			if wave == "groupA_Y3":
				fmriName = subject[1:3]
			
			if wave == "groupB_Y3": 
				fmriName = subject[1:4]

			print subject, fmriName

			fmriDir = "/Volumes/MusicProject/Longitudinal_study/Functional/%s/%s" %(wave,group)
			fmriList = [elem for elem in os.listdir(fmriDir) if "." not in elem]
			for name in fmriList:  
				if name.startswith(fmriName): 
					#print 'Found a match! %s is %s' %(subject,fmriName)
					fmriSubjName = name

			fmriSubjFolder = "/Volumes/MusicProject/Longitudinal_study/Functional/%s/%s/%s" %(wave,group,fmriSubjName)
			
			if os.path.exists(fmriSubjFolder):
				print fmriSubjFolder

			if os.path.exists(checkfile):
				print sectionColor2 + "Subject %s already has EV files. Moving on%s" %(subject,mainColor)
				continue

			logfiles = [elem for elem in os.listdir(subjfolder) if ".DS" not in elem] 
			run = 0
			
			for log in logfiles:
				run = run + 1
				print yellow + '%s\t%d%s' %(subject,run,mainColor)
				logfile = subjfolder + log
				incong_evfile = fmriSubjFolder + "/ev_incong_run%d.txt" %(run)
				cong_evfile = fmriSubjFolder + "/ev_cong_run%d.txt" %(run)

				df = pd.read_csv(logfile, sep = '\t', parse_dates = True, header = None, names = ["onset","colorword","colorink","reaction","reaction2"], skip_blank_lines = True) 
				
				con1_s = df.onset[0]
				incon1_s = df.onset[12]
				con2_s = df.onset[24]
				incon2_s = df.onset[36]
				con3_s = df.onset[48]
				incon3_s = df.onset[60]

				con1_e = df.onset[11] + 1.7
				con2_e = df.onset[11+12+12] + 1.7
				con3_e = df.onset[11+12+12+12+12] + 1.7
				incon1_e = df.onset[11+12] + 1.7
				incon2_e = df.onset[11+12+12+12] + 1.7
				incon3_e = df.onset[11+12+12+12+12+12] + 1.7

				# con1_e = df.reaction2[11]
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

				c1l = con1_e - con1_s
				c2l = con2_e - con2_s
				c3l = con3_e - con3_s

				ic1l = incon1_e - incon1_s
				ic2l = incon2_e - incon2_s
				ic3l = incon3_e - incon3_s

				if c1l or c2l or c3l or ic1l or ic2l or ic3l < 22:
					print red + "Found a trial where the block lenth is unusual short: %s, run %d%s" %(subj,run,mainColor)

				cong_mat = np.array([ [con1_s,c1l,1], [con2_s,c2l,1], [con3_s,c3l,1] ])
				print cong_mat
				print
				np.savetxt(cong_evfile, cong_mat, fmt = '%1.5f', delimiter='\t')

				incong_mat = np.array([ [incon1_s,ic1l,1], [incon2_s,ic2l,1], [incon3_s,ic3l,1] ])
				print incong_mat
				print
				np.savetxt(incong_evfile, incong_mat, fmt = '%1.5f', delimiter='\t')







