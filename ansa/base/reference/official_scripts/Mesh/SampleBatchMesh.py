#
#==================================================
#*		 HEADER
#==================================================
#
#Developed by: Stamatis Karastamatiadis
#Date: 02/02/2016
#
#		BETA CAE Systems
#		Kato Scholari, Thessaloniki,
#		GR-57500, Epanomi,
#		Greece
#		Tel: +302392021420 , +302311993300
#		Fax: +302392021417
#		E-mail: ansa@beta-cae.com
#		URL: http://www.beta-cae.com
#
#		Copyright (c) 2016 BETA CAE Systems
#		All rights reserved.
#
#=================================================
#*		DISCLAIMER
#=================================================
#
# BETA CAE Systems assumes no responsibility or 
# liability for any damages, errors, inaccuracies 
# or data loss caused by installation or use of this 
# software.
#
#=================================================
#*		HISTORY
#=================================================
#
#Date:                     Updater: 
#Modifications:
#-------------------------------------------------
#Date:                     Updater:
#Modifications:
#-------------------------------------------------
#
#
#
#Name: 			SampleBatchMesh
#Description: Reads from a directory the ansa_mpar and the ansa_qual files,
#						creates a session, adds all parts of the database in the session,
#						runs the session and exports statistics report in the same 
#						directory.

import ansa
from ansa import base
from ansa import utils
from ansa import constants
from ansa import batchmesh

@ansa.session.defbutton('MESH', 'SampleBatchMesh')
def SampleBatchMeshMain():
	
	'''Reads from a directory the ansa_mpar and the ansa_qual files,
creates a session, adds all parts of the database in the session,
runs the session and exports statistics report in the same 
directory. The statistics file is exported in the html format.
The  ansa_mpar file must be called "sample_parameters.ansa_mpar"
and the ansa_qual file must be called "sample_quality.ansa_qual".
	'''
	print("Please select the directory where the sample_parameters.ansa_mpar and sample_quality.ansa_qual files are located:")
	dir_path = utils.SelectOpenDir("")
	if not dir_path:
		print("No directory has been selected!")
		return
	else:
		print("Selected directory: "+dir_path)
	session = batchmesh.GetNewSession()
	
	parameters = batchmesh.ReadSessionMeshParams(session,dir_path+"sample_parameters.ansa_mpar")
	if parameters == 0:
		print("The file sample_parameters.ansa_mpar doesn't exist!")
		return
	else:
		print("Reading sample_parameters.ansa_mpar file.")
	criteria = batchmesh.ReadSessionQualityCriteria(session,dir_path+"sample_quality.ansa_qual")
	if criteria == 0:
		print("The file sample_quality.ansa_qual doesn't exist!")
		return
	else:
		print("Reading sample_quality.ansa_qual file.")
		
	parts = base.CollectEntities(constants.NASTRAN, None, "ANSAPART")
	for part in parts:
		batchmesh.AddPartToSession(part, session)
	
	session_status = batchmesh.RunSession(session)
	if session_status == 1:
		print("Session has run.")
	elif session_status == 2:
		print("Session hasn't run!")
	ret_val = batchmesh.WriteStatistics(session,dir_path+"statistics_report.html")
	if ret_val == 1:
		print("Quality violations and/or unmeshed macro(s) remain!")
		print("Report saved in "+dir_path+" statistics_report.html.")
	print("Process completed.")
