'''
==================================================
*                    HEADER
==================================================

Developed by:Michael Tryfonidis
Date:26/01/2011

                                 BETA CAE Systems
                      Kato Scholari, Thessaloniki,
                                GR-57500, Epanomi,
                                           Greece
               Tel: +302392021420 , +302311993300
                               Fax: +302392021417
                         E-mail: ansa@beta-cae.com
                      URL: http://www.beta-cae.com

 	      Copyright (c) 2011 BETA CAE Systems 
                              All rights reserved.

=================================================
*                   DISCLAIMER
=================================================

 BETA CAE Systems assumes no responsibility or 
 liability for any damages, errors, inaccuracies 
 or data loss caused by installation or use of this 
 software.

=================================================
*                    HISTORY
=================================================

Date: 14/09/2011      Updater:Giannis Haralampidis      
Modifications: A scenario contains now the meshing sessions.
               Built in filtering criteria were added to each meshing session.
-------------------------------------------------
Date:                 Updater:
Modifications:
-------------------------------------------------
'''


'''
Name:SampleProject
Description: 	1.Opens CAD-files and save as *.ansa in same directory.
 	     		2.Merges all *.ansa files.
             	3.Offset to middle surface.
            	4.Reads and realize Connection Points.A vip file with the name "weldfile.vip" 
	       		must be located in the given directory.  
             	5.Creates a Batch Meshing Scenario and sessions and assigns the mesh parameters 
				and qualitycriteria. The parts are added to batch mesh sessions according to 
				some filteriing criteria.This part of the script should be changed according to 
				the user needs.
	       		The  ansa_mpar files must be called "FRONT.ansa_mpar","FLOOR_REAR.ansa_mpar",
				"ROOF_OUTPAN.ansa_mpar"
	       		The  ansa_qual file must be called "Sample_Quality_Criteria.ansa_qual"
             	6.Runs Batch Mesh
             	7.Saves the Error Statistics
	     		8.Exports in nastran.
	      		-The directory that contains all the files must be selected when the file manager will open-
'''

import glob
import ansa
from ansa import base
from ansa import mesh
from ansa import utils
from ansa import batchmesh as bm
from ansa import connections
from ansa import session

@ansa.session.defbutton('MESH', 'SampleProject')
def SampleProjectMain():
	
	"""1.Opens CAD-files and save as *.ansa in same directory.
	2.Merges all *.ansa files.
	3.Offset to middle surface.
	4.Reads and realize Connection Points.A vip file with the name "weldfile.vip" 
	  must be located in the given directory.  
	5.Creates a Batch Meshing Scenario and sessions and assigns the mesh parameters 
	and quality criteria. The parts are added to batch mesh sessions according to 
	some filteriing criteria.This part of the script should be changed according 
	to the user needs. The  ansa_mpar files must be called "FRONT.ansa_mpar",
	"FLOOR_REAR.ansa_mpar","ROOF_OUTPAN.ansa_mpar" The  ansa_qual file must be 
	called "Sample_Quality_Criteria.ansa_qual"
	6.Runs Batch Mesh
	7.Saves the Error Statistics
	8.Exports in nastran.
	 -The directory that contains all the files must be selected when the file manager will open-
	"""

	print("Please select the directory  where all the files are located");	
	dir_path = utils.SelectOpenDir("")
	if not dir_path:
		return
	_TranslateCadToAnsaS(dir_path)
	session.New("discard")
	_MergeInDirS(dir_path)
	base.OffsetLink(0.5)
	connections.ReadConnections("VIP", dir_path+"weldfile.vip")

	#Create Batch Mesh Sessions and assign the parameters
	
	scenario = bm.GetNewMeshingScenario("MeshProject")
	sessions = [bm.GetNewSession("Name","FRONT"), 
				bm.GetNewSession("Name","FLOOR_REAR"),
				bm.GetNewSession("Name","ROOF_OUTPAN")]
	FRONT 		= sessions[0]
	FLOOR_REAR 	= sessions[1]
	ROOF_OUTPAN	= sessions[2]
	
	bm.AddSessionToMeshingScenario(sessions,scenario)

	bm.ReadSessionMeshParams(FRONT,dir_path+"FRONT.ansa_mpar")
	bm.ReadSessionQualityCriteria(FRONT, dir_path+"Sample_Quality_Criteria.ansa_qual")

	bm.ReadSessionMeshParams(FLOOR_REAR,dir_path+"FLOOR_REAR.ansa_mpar")
	bm.ReadSessionQualityCriteria(FLOOR_REAR, dir_path+"Sample_Quality_Criteria.ansa_qual")

	bm.ReadSessionMeshParams(ROOF_OUTPAN,dir_path+"ROOF_OUTPAN.ansa_mpar")
	bm.ReadSessionQualityCriteria(ROOF_OUTPAN, dir_path+"Sample_Quality_Criteria.ansa_qual")

 
	#Assign the right parts to the respective Session

	bm.AddFilterToSession("COG x","is less than","400",FRONT)
	
	bm.AddFilterToSession("Module Id","is in range x/y","20/30",FLOOR_REAR,"Match","any")
	bm.AddFilterToSession("Module Id","is in range x/y","40/50",FLOOR_REAR,"Match","any")
	
	bm.AddFilterToSession("Module Id","is in range x/y","10/20",ROOF_OUTPAN,"Match","any");
	bm.AddFilterToSession("Module Id","is in range x/y","50/60",ROOF_OUTPAN,"Match","any");
	
	parts = base.CollectEntities(constants.NASTRAN, None, "ANSAPART")
	for part in parts:
		bm.AddPartToMeshingScenario(part,scenario)
	
	base.SaveAs(dir_path+"all_together_before_batch_mesh.ansa")
	
	bm.RunMeshingScenario(scenario,120)
	bmWriteStatistics(FRONT,dir_path+"Error_stats_FRONT.inf");
	bm.WriteStatistics(FLOOR_REAR,dir_path+"Error_stats_FLOOR_REAR.inf");
	bm.WriteStatistics(FLOOR_REAR,dir_path+"Error_stats_ROOF_OUTPAN.inf");
	bm.Save()
	output_file = dirpath+"batchmeshed.nas"
	base.OutputNastran(filename=output_file)
	print("Execution of SampleProject ended")


'''
Name:TranslateCadToAnsaS
Description:Opens iges files and save as *.ansa in same directory
Example:TranslateCadToAnsaS("home/mydir/");
'''


def _TranslateCadToAnsaS(dir_path):
	session.New("discard")
	
	for file in glob.glob(dir_path+"*.iges"):
		print("Opening file: "+file)
		base.Open(file)
		base.Save()

'''
Name:MergeInDirS
Description:Merges files located in a specific directory
Example:MergeInDirS("home/mydir/");
'''

def _MergeInDirS(dir_path):

	for file in glob.glob(dir_path+"*.ansa"):
		print("Merging file: "+file)
		utils.Merge(file)
	
