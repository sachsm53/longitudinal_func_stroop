#!/usr/bin/env python

import os,sys
from commando import commando
from commando import writeToLog
import argparse
import re
from datetime import datetime
from subprocess import call
from subprocess import check_output
import csv as csv 
import numpy as np
from scipy import stats



# #create ROI on standardized brain 

#Cluster 5 is the cluster of interest: 
# Cluster Index	Voxels	P	-log10(P)	Z-MAX	Z-MAX X(mm)	Z-MAX Y(mm)	Z-MAX Z(mm)	Z-COG X(mm)	Z-COG Y(mm)	Z-COG Z(mm)	COPE-MAX	COPE-MAX X(mm)	COPE-MAX Y(mm)	COPE-MAX Z(mm)	COPE-MEAN
# 5		1532	5.72e-06	5.24		5.44	-2			6			52			0.385		11.9		45.9		61.7		2				20				64				27.9

# fslmaths /usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz -mul 0 -add 1 -roi 46 1 66 1 62  1 0 1 cluster5_point -odt float
# fslmaths cluster5_point.nii.gz -kernel sphere 8 -fmean cluster5_sphere -odt float


## Create new ROI on standardized brain based on correct coordinates from 44s. 

Cluster 3 (in the incongruent - congruent ALL subjects) is the cluster of interest: 

Cluster Index	Voxels	P	-log10(P)	Z-MAX	Z-MAX X (mm)	Z-MAX Y (mm)	Z-MAX Z (mm)	Z-COG X (mm)	Z-COG Y (mm)	Z-COG Z (mm)	COPE-MAX	COPE-MAX X (mm)	COPE-MAX Y (mm)	COPE-MAX Z (mm)	COPE-MEAN
3	1552	4.89e-06	5.31	5.34	-2	2	58	0.0676	12.3	46.5	61.5	2	20	64	28.3


fslmaths /usr/local/fsl/data/standard/MNI152_T1_2mm_brain.nii.gz -mul 0 -add 1 -roi 46 1 64 1 65  1 0 1 /Volumes/MusicProject/Longitudinal_study/Functional/sma_cluster_point_new -odt float
fslmaths /Volumes/MusicProject/Longitudinal_study/Functional/sma_cluster_point_new -kernel sphere 8 -fmean /Volumes/MusicProject/Longitudinal_study/Functional/sma_cluster_sphere_new -odt float
fslmaths /Volumes/MusicProject/Longitudinal_study/Functional/sma_cluster_sphere_new -bin /Volumes/MusicProject/Longitudinal_study/Functional/sma_cluster_sphere_new_bin


## Create ROI from coordinates in meta-analysis 

#1) Derrfuss et al. 
Inferior frontal junction (6/8/44), left: -40,4,32 (Talairach) --> -41,4,33
ACC/pre-SMA (32/6), right: 2,14,42 (Talairach) --> 2,12,46
ACC/SFG (32/9), left: -2, 36, 26 --> -2, 37, 28

#2) Laird et al 2005
anterior cingulate --> (2,16,41) --> 2,14,45
left IFJ --> -44,6,34 --> -45,6,36
rostal cingulate zone posterior --> 2,16,41 --> 2,14,45
rostral cingulate zone anterior (-3,37,25) --> -3,38,27



## Extract the Percent Signal Change for the ROI for each subject (1-4-2017)

#logging colors

sectionColor = "\033[94m"
sectionColor2 = "\033[96m"
mainColor = "\033[92m"

#set locations
datafolder = "/Volumes/MusicProject/Longitudinal_study/Functional/"
#roifile = datafolder + "reg_yearsmus/reg_emo_yearsmus_apos_aneg.gfeat/cope1.feat/cluster_mask_zstat2.nii.gz"
#rois = ["cluster5_sphere.nii.gz"]
rois = ['sma_cluster_sphere_new_bin']

copeList = ["cope2.feat","cope3.feat","cope5.feat"]

#Cope1 = all 
#Cope2 = C 
#Cope3 = I  
#Cope4 = C - I
#Cope5 = I - C

for roi in rois: 

	print roi

	roifile = datafolder + roi

	copecount = 0 

	for cope in copeList:

		copecount = copecount + 1
		if copecount == 1: 
			copename = "C-rest_cope2"
		elif copecount == 2:
			copename = "I-rest_cope3"
		elif copecount == 3: 
			copename = "I-C_cope5"

		outfile = datafolder + "featquery_smacluster_%s.csv" %(copename)
		headers = ['subject','cope','voxels','min','10%','mean','median','90%','max','stdev']
		resultfile = open(outfile, 'w')
		writefile = csv.writer(resultfile)
		writefile.writerow(headers)
		resultfile.close()
		waves = ["groupA_Y3", "groupB_Y3"]
		count = 0

		for wave in waves: 
			print '%s%s\n' %(wave,mainColor)
			groupList = ['Control', 'Music', 'Sport']

			for group in groupList:
				subjectDir = "/Volumes/MusicProject/Longitudinal_study/Functional/%s/%s/" %(wave,group)
				subjectList = [elem for elem in os.listdir(subjectDir) if "." not in elem] 
				excludeList = ['19_8042AD_LE','108-IM','07_7993AD_JS','111-AM','02_7877AD_SS','07_7946Ad_GP','28_8019Ad_JZ','109-RS','105-MJ','14_8072Ad_BM']
				subjectList = [elem for elem in subjectList if elem not in excludeList]
				subjectList.sort()
				#print subjectList

				for subj in subjectList:
					subject = subj

					#define files and folders here, in case a particular step is skipped
					subjfolder = subjectDir + subject + "/"
					secondlevel_featfolder = subjfolder + "secondlevel_cor_stroop.gfeat/"
					cope_featfolder = secondlevel_featfolder + cope
					logfile = subjfolder + "/analysis_log.txt"
					csvline = []
					csvline.append(subject)
					csvline.append(cope_featfolder)
					subj_featquery_folder = "featquery_smacluster_%s" %(copename)
					featquery_report = cope_featfolder + "/featquery_smacluster_%s/report.txt" %(copename)

					if not os.path.exists(featquery_report):
						command = "featquery 1 %s 1 stats/pe1 %s -p -s %s" %(cope_featfolder,subj_featquery_folder,roifile)
						print sectionColor + 'Doing featquery using %s mask for %s, group %s, featfolder %s%s' %(roi,subject,group,copename,mainColor)
						commando(command,logfile)

					else: 
						print sectionColor + 'Folder already found. %s already completed %s' %(subject,mainColor)

					with open(featquery_report, 'r') as txtfile:
						resultfile = open(outfile,'a')		

						for line in txtfile:
							csvline.extend(line.split()[2:10])
							print sectionColor + "Writing results out to log file%s" %mainColor
							print csvline
							writefile = csv.writer(resultfile)
							writefile.writerow(csvline)
						resultfile.close()
