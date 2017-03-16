#!/usr/bin/env python

import os,sys

from commando import commando

from commando import writeToLog

import argparse

import numpy as np

import re

from datetime import datetime

from subprocess import call

from subprocess import check_output

import csv

#parse command line arguments

parser = argparse.ArgumentParser()

parser.add_argument("--nopre",help="skip all preprocessing steps", action="store_true")

parser.add_argument("--noconvert",help="skip converting from DICOM to NIFTI", action="store_true")

parser.add_argument("--nobet",help="skip brain extraction", action="store_true")

parser.add_argument("--noreg",help="skip registration copying", action="store_true")

parser.add_argument("--nofirst",help="skip first level feat", action="store_true")

parser.add_argument("--nosecond",help="skip second level feat", action="store_true")

args = parser.parse_args()

#set locations

datafolder = "/Volumes/MusicProject/Longitudinal_study/Functional/"

genericdesign_scrub = "/Volumes/MusicProject/Longitudinal_study/Functional/firstlevel_design_scrub.fsf"

genericdesign_noscrub = "/Volumes/MusicProject/Longitudinal_study/Functional/firstlevel_design_noscrub.fsf"

secondleveldesign = "/Volumes/MusicProject/Longitudinal_study/Functional/secondlevel_design_stroop.fsf"

#fixdesign = "/Volumes/External/Music_training/stroop/firstlevel_stats_design.fsf"

#genericdesign = "/Volumes/External/cross_fmri/run1_design.fsf"



#set analysis values

numconfounds = 8

smoothmm = 5	#smoothing sigma fwhm in mm

smoothsigma = smoothmm/2.3548	#convert to sigma

additive = 10000	#value added to distinguish brain from background

brightnessthresh = additive * .75



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

count = 0

for wave in waves: 

	print pink + '%s%s\n' %(wave,mainColor)

	groupList = ['Control', 'Music', 'Sport']

	for group in groupList:

		subjectDir = "/Volumes/MusicProject/Longitudinal_study/Functional/%s/%s/" %(wave,group)

		subjectList = [elem for elem in os.listdir(subjectDir) if "." not in elem] 

		subjectList.sort()

		# if group == 'Control': 

		# 	# excludeList = ["05_7980AD_BP","07_7993AD_JS", "11_7964AD_RL"]

		# 	# subjectList = [elem for elem in subjectList if elem not in excludeList]

		# 	#subjectList = ["19_8042AD_LE"]

		# elif group == 'Music': 

		# 	# excludeList = ["02_7877AD_SS","04_7861AD_MA"]

		# 	# subjectList = [elem for elem in subjectList if elem not in excludeList]

		# 	#subjectList = ["06_7853AD_JR"]

		# elif group == 'Sport': 

		# 	excludeList = ["07_7946Ad_GP","14_8072Ad_BM","22_7988Ad_GH","28_8019Ad_JZ"]

		# 	subjectList = [elem for elem in subjectList if elem not in excludeList]


		#subjectList = ["01_7982AD_JG"]

		#print groupColor + '%s group%s' %(group,mainColor)

		#print group

		for subj in subjectList:

			subject = subj

			#define files and folders here, in case a particular step is skipped

			subjfolder = subjectDir + subject + "/"

			#print subjfolder

			#print yellow + 'Starting on %s group %s %s' %(group,subject,mainColor)

			logfile = subjfolder + "analysis_log.txt"

			#Skip this subject if they do not have ev files 

			checkevfile = subjfolder + "ev_cong_run2.txt"

			finalfile = subjfolder + "secondlevel_cor_stroop.gfeat/cope1.feat" 

			if os.path.exists(finalfile):

				count = count + 1

				print count, finalfile


			if not os.path.exists(checkevfile): 

				print sectionColor + "The subject %s has no EV Files. Moving on%s" %(subject,mainColor)

				print

				continue


			# #Brain Extraction

			mprage = subjfolder + "coMPRAGEKids.nii.gz"

			t1image = subjfolder + "mprage_brain.nii.gz"

			if not args.nobet:

				if not os.path.exists(t1image):

					print sectionColor + "Skull Striping for %s%s"  % (subject,mainColor)

					command = "/Volumes/MusicProject/Longitudinal_study/Functional/skullstrip.py %s" %subjfolder

					print command

					call(command,shell = True)
				
				else: 

					print sectionColor + "Already skullstripped %s, moving on %s"  % (subject,mainColor)


			#First level analysis 

			if not args.nofirst:

				for run in range(1,3):

					#print run

					origdata = "stroop_run%d.nii.gz" %(run)

					firstlevel_featfolder = subjfolder + "firstlevel_stroop_cor_run%d.feat" %(run)

					inputfile = subjfolder + "stroop_run%d.nii.gz" %(run)

					#outputfile = subjfolder + "firstlevel_design_run%d.fsf" %run

					designOutput = subjfolder + "firstlevel_stroop_cordesign_run%d.fsf" % (run)

					checkfile = firstlevel_featfolder + "/rendered_thresh_zstat5.nii.gz"

					#print checkfile

					# designfile = firstlevel_folder + "/design.mat"

					# reportfile = firstlevel_folder + "/report.html"

					
					# DVARS Scrubbing Motion Correction

					scrubout = subjfolder + "scrub_confounds_run%d" %(run)

					metric_values_text = subjfolder + "scrub_metric_values_run%d" %(run)

					metric_values_plot = subjfolder + "scrub_metric_plot_run%d" %(run)

					if not os.path.exists(metric_values_plot):

						command = "fsl_motion_outliers -i %s -o %s --dvars -s %s -p %s -v" % (inputfile, scrubout, metric_values_plot, metric_values_plot)

						print sectionColor + "FSL Motion Outliers for %s, run %d%s"  % (subject,run,mainColor)

						commando(command, logfile)

					else: 

						print sectionColor + "FSL Motion Outliers already completed for %s, run %d. Moving on%s"  % (subject,run,mainColor)

					# if os.path.exists(scrubout):
					# 	with open(scrubout) as f:
					# 		reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
					# 		first_row = next(reader)
					# 		num_cols = len(first_row)
					# 		print '%s\trun%d\t%d' %(subj,run,num_cols)

					# else: 

					# 	print '%s\trun%d\t%d' %(subj,run,0)

					print sectionColor2 + "First level FEAT Analysis for: %s, run: %d%s"  % (subject,run,mainColor)

					if os.path.exists(checkfile):

						print checkfile

						print sectionColor + "First level feat analysis already completed for %s, run %d. Moving on.%s"  % (subject,run,mainColor)

						continue 

					if not os.path.exists(inputfile):

						print sectionColor + "Run %s for subject %s does not exist or is not in folder. Moving on.%s" %(run,subject,mainColor)

						continue

					# Get number of volumes: 

					command = 'fslinfo %s' %(inputfile)

					results = check_output(command,shell=True)

					numtimepoints = results.split()[9]

					print "Number of volumes: %s" %(numtimepoints)

					
					#set up evfiles 

					evfile1 = subjfolder + "ev_cong_run%d.txt" %(run)

					evfile2 = subjfolder + "ev_incong_run%d.txt" %(run)


					#Split based on who has a scrub confound file

					if os.path.exists(scrubout):

						print sectionColor + "This subject has a scrub folder %s%s" %(scrubout,mainColor)

						command = "sed -e 's/DEFINEINPUT/%s/g' -e 's/DEFINEOUTPUT/%s/g' -e 's/DEFINESCRUB/%s/g' -e 's/DEFINESTRUCT/%s/g' -e 's/DEFINEVOLUME/%s/g' -e 's/DEFINEEVFILE1/%s/g' -e 's/DEFINEEVFILE2/%s/g' %s > %s" % (re.escape(inputfile),re.escape(firstlevel_featfolder), re.escape(scrubout),re.escape(t1image), numtimepoints,re.escape(evfile1),re.escape(evfile2),genericdesign_scrub,designOutput)

						commando(command, logfile)

						command = "feat %s" % designOutput

						commando(command, logfile)

					else: 

						print sectionColor + "No scrub folder found for run %d%s" %(run,mainColor)

						command = "sed -e 's/DEFINEINPUT/%s/g' -e 's/DEFINEOUTPUT/%s/g' -e 's/DEFINESTRUCT/%s/g' -e 's/DEFINEVOLUME/%s/g' -e 's/DEFINEEVFILE1/%s/g' -e 's/DEFINEEVFILE2/%s/g' %s > %s" % (re.escape(inputfile),re.escape(firstlevel_featfolder), re.escape(t1image), numtimepoints,re.escape(evfile1),re.escape(evfile2),genericdesign_noscrub,designOutput)

						commando(command, logfile)

						command = "feat %s" % designOutput

						commando(command, logfile)


			# 	# #prepare web page report

			# 	# timestart= datetime.now()

			# 	# timestamp = timestart.strftime('%b %d %G %I:%M%p')

			# 	# fsldir = os.environ['FSLDIR']

			# 	# writeToLog("<html><head><title>Resting State Analysis Report "+subject+"</title><link REL=stylesheet TYPE=text/css href="+fsldir+"/doc/fsl.css></head><body>",reportfile)

			# 	# writeToLog("\n<h1>Resting State Analysis for "+subject+"</h1>Processing started at: "+timestamp+"<br><hr><br>",reportfile)

			# 	# call("open " + reportfile,shell=True)


			# 	# command = "sed -e 's/DEFINESUBJECT/%s/g' -e 's/DEFINEINPUT/%s/g' -e 's/DEFINEGROUP/%s/g' -e 's/DEFINEVOLUME/%s/g' -e 's/DEFINERUN/%s/g' %s > %s" % (subject,re.escape(inputfile), group, numtimepoints,origdata,genericdesign,outputfile)

			# 	# commando(command,logfile)


			# 	# "/Volumes/External/Music_training/stroop/DEFINEGROUP/DEFINESUBJECT/firstlevel_DEFINERUN"
			# 	# "/Volumes/External/Music_training/stroop/DEFINEGROUP/DEFINESUBJECT/DEFINERUN"
			# 	# "/Volumes/External/Music_training/stroop/DEFINEGROUP/DEFINESUBJECT/mprage_brain.nii.gz"

			# 	# if os.path.exists(featfolder:

			# 	# 	print 'Already did %s, you silly goose!' %(featfolder)

			# 	# 	continue 

			

			# 	commando(command,logfile)


			# 	command = "feat %s" % outputfile

			# 	commando(command,logfile)



			#second level analysis 

			if not args.nosecond:

				secondlevel_folder = subjfolder + "secondlevel_cor_stroop.gfeat"

				feat1 = subjfolder + 'firstlevel_stroop_cor_run1.feat'

				feat2 = subjfolder + 'firstlevel_stroop_cor_run2.feat'

				if not os.path.exists(feat1) or not os.path.exists(feat2):

						print sectionColor + "One or more first level feat folders did not complete correctly or does not exist for subject %s. Moving on.%s" %(subject,mainColor)

						continue

				#read in the data from the motion report file 1
				filename = feat1 + '/report_prestats.html'
				textfile = open(filename,'r')
				filetext = textfile.read()
				textfile.close()
				#find absolute motion
				result_ab1 = re.search('absolute=(.*)mm,',filetext)
				motion_ab1 = result_ab1.groups()[0]
				#find relative motion
				result_rel1= re.search('relative=(.*)mm',filetext)
				motion_rel1 = result_rel1.groups()[0]
				print red + "%s\t%d\t%s\t%s%s" %(subject,1,motion_ab1,motion_rel1,mainColor)

				#read in the data from the motion report file 2
				filename2 = feat2 + '/report_prestats.html'
				textfile2 = open(filename2,'r')
				filetext2 = textfile2.read()
				textfile2.close()
				#find absolute motion
				result_ab2 = re.search('absolute=(.*)mm,',filetext2)
				motion_ab2 = result_ab2.groups()[0]
				#find relative motion
				result_rel2 = re.search('relative=(.*)mm',filetext2)
				motion_rel2 = result_rel2.groups()[0]
				print red + "%s\t%d\t%s\t%s%s" %(subject,2,motion_ab2,motion_rel2,mainColor)

				checkcopefolder = secondlevel_folder + "/cope5.feat/rendered_thresh_zstat1.nii.gz"

				print sectionColor2 + "Second Level Analysis for: %s, run: %d%s"  % (subject,run,mainColor)

				if not os.path.exists(checkcopefolder):

					designOutput2 = subjfolder + "secondlevel_stroop_design.fsf"

					command = "sed -e 's/DEFINEOUTPUT/%s/g' -e 's/DEFINEFEAT1/%s/g' -e 's/DEFINEFEAT2/%s/g' %s > %s" % (re.escape(secondlevel_folder),re.escape(feat1), re.escape(feat2),secondleveldesign,designOutput2)

					commando(command,logfile)

					command = "feat %s" % designOutput2

					commando(command,logfile)

				else: 

					#print checkcopefolder

					print sectionColor + "Second level for %s already completed, moving on %s\n"  % (subject,mainColor)

			

			## First-Level Analysis after ICA (only stats portion)

			# for run in range(1,2):

			# 	#print run

			# 	icafolder = subjfolder + 'run%d.ica' %(run)

			# 	#print icafolder

			# 	fix_featfolder = subjfolder + "firstlevel_stroop_run%d_fix.feat" %(run)

			# 	inputfile = icafolder + "/filtered_func_data_clean.nii.gz"

			# 	command = 'fslinfo %s' %(inputfile)

			# 	results = check_output(command,shell=True)

			# 	numtimepoints = results.split()[9]

			# 	print numtimepoints


			# 	if not os.path.exists(inputfile):

			# 		print sectionColor2 + "You have not run FIX for subject %s, run %s!%s" %(subject,run,mainColor)

			# 	outputfile = "%s/firstlevel_fix_design_run%d.fsf" % (subjfolder,run)

			# 	print sectionColor + "Working on subject %s, run %s%s"  % (subject,run,mainColor)

			# 	# if not os.path.exists(firstlevel_folder):

			# 	# 	command = "mkdir %s" % firstlevel_folder

			# 	# 	call(command,shell=True)

			# 	command = "sed -e 's/DEFINEINPUT/%s/g' -e 's/DEFINEVOLUME/%s/g' -e 's/DEFINEOUTPUT/%s/g' %s > %s" % (re.escape(inputfile),numtimepoints,re.escape(fix_featfolder),fixdesign,outputfile)

			# 	commando(command,logfile)

			# 	command = "feat %s" % outputfile

			# 	# command = "melodic -i %s -o %s --nobet -d 25 -report" %(inputfile, outputdir)

			# 	commando(command,logfile)

			# 	regdir = subjfolder + "firstlevel_stroop_run%d.feat/reg" %(run)

			# 	regstand = subjfolder + "firstlevel_stroop_run%d.feat/reg_standard" %(run)

			# 	if not os.path.exists(regdir):

			# 		print sectionColor + "Can't find %s, run %s reg folder%s" %(subject,run,main)

			# 	if not os.path.exists(regstand):

			# 		print sectionColor + "Can't find %s, run %s reg_standard folder%s" %(subject,run,main)

			# 	print sectionColor2 + "Copying %s to %s%s" %(regdir,fix_featfolder, mainColor)

			# 	command = "cp -r %s %s/reg" % (regdir,fix_featfolder)

			# 	commando(command,logfile)

			# 	command = "cp -r %s %s/reg_standard" % (regstand,fix_featfolder)

			# 	commando(command,logfile)











			

			

