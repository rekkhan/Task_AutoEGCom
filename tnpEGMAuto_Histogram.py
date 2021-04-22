# + Usage:
# *python   tnpEGM_commissioningRun2017BUL_DF.py   &> log2017FUL.txt &



import sys
import os
from os import listdir
from os.path import isfile, isdir, join
import math
import re

import ROOT
from ROOT import gStyle
from ROOT import gROOT

import Lib_Python.tool_InfoCollector as collector

ROOT.gROOT.SetBatch(True)




# + Import function from file
#============================
list_funcUsrDef = []
list_funcUsrDef = collector . Get_listFunction ("UserDefined")

for function in list_funcUsrDef:
	ROOT . gInterpreter . Declare (str(function))
	#print ("  ******  the function is:")
	#print ("{}\n\n" . format(function))
	pass










# + Loop over the tree
#=====================
def Create_Histogram (path_input, isMC, path_PU, tree_PU, dir_hist, path_hist):
	# + Information for input
	#------------------------
	usephoid = False
	
	treename = 'tnpEleIDs/fitter_tree'
	
	if usephoid:
		treename = 'tnpPhoIDs/fitter_tree'
		pass
	
	
	
	# + Open input file
	#------------------
	print("     || -- Processing file {} ..." . format(path_input))
	
	file_input = ROOT.TFile . Open (path_input, "read")
	tree_input = file_input . Get (treename)
	
	
	
	# + Get PU tree if required
	#--------------------------
	if (path_PU.lower() != "ignore"):
		friendTreeName = tree_PU
		tree_input . AddFriend (friendTreeName, path_PU)
		pass
	
	dataFrame = ROOT.RDataFrame(tree_input)
	
	#print "PRINTING DATAFRAME"
	#print(dataFrame.GetColumnNames())
	
	if (path_PU.lower() != "ignore"):
		print ("     ||    |--> PU weight found, getting weight from {}.totWeight" . format(friendTreeName))
		dataFrame = dataFrame.Define ("ev_weight", "{}.totWeight" . format(friendTreeName))
		pass
	else:
		print ("     ||    |--> No PU weight required, all weights are set to 1.0")
		dataFrame = dataFrame.Define ("ev_weight", "1.0")
		pass
	
	
	
	# + Get the user-define variables
	#--------------------------------
	list_varUsrDef = []
	list_varUsrDef = collector . Get_listJson("UserDefined/usrDefVars.json")
	
	for varUsrDef in list_varUsrDef:
		myVar = str(varUsrDef["variable"])
		myForm = str(varUsrDef["formula"])
		
		#print ("     || **** {:20} = {}" . format (myVar, myForm))
		
		dataFrame = dataFrame . Define (myVar, myForm)
		pass
	
	
	
	# + Create path for output
	#-------------------------
	if not os.path.exists(dir_hist):
		print ("     ||    |--> Output directory {0} is missing, now creating ..." . format (dir_hist))
		os.makedirs (dir_hist)
		pass
	else:
		print ("     ||    |--> Output directory {0} is available" . format (dir_hist))
		pass
	
	
	
	# + Get the filter for creating histogram
	#----------------------------------------
	list_histAll = []
	
	for obj in listdir ("UserDefined"):
		if obj . startswith ("usrDefHist"):
			pathJson = "UserDefined/{}" . format (obj)
			
			print ("     ||    |--> Reading json: {}" . format(pathJson))
			
			list_histByCat = []
			list_histByCat = collector . Get_listJson(pathJson)
			
			list_histAll . append (list_histByCat)
			pass
		pass
	
	
	
	# + Create the dictionary of histograms
	#--------------------------------------
	histList = {}
	
	# * Fill the histograms
	print ("     ||    |--> Filling the histograms")
	
	ilist = 0
	for list_histByCat in list_histAll:
		ilist += 1
		print ("     ||    |     [*] Filling the histograms from set #{:02d} ..." . format(ilist))
		fillHists (dataFrame, histList, list_histByCat)
		pass
	
	file_input . Close()
	
	
	
	
	# + Create output root file
	#--------------------------
	namefile_isMC = ["DT", "MC"]
	
	print ("     ||    |--> Creating output file: {} ..." . format (path_hist))
	file_output = ROOT.TFile("{}".format (path_hist), "RECREATE")
	
	file_output . cd()
	
	for key in histList:
		histList[key] . Write()
		pass
	
	file_output . Write()
	file_output . Close()
	
	print ("     ||    |--> Output file {} has been saved" . format (path_hist))
	
	pass










# + Fill histograms using RDataFrame
#===================================
def fillHists (dataFrame, histList, list_histByCat):
	dataFrameHist = dataFrame
	nHistInCat = len(list_histByCat)
	
	regECAL = ""
	
	for info in list_histByCat[0]:
		if "filter" in info:
			dfFilter = str(list_histByCat[0][info])
			print ("     ||    |       $ {} is:  {} " . format(info, dfFilter))
			dataFrameHist = dataFrameHist.Filter (dfFilter)
			pass
		elif "regECAL" in info:
			regECAL = list_histByCat[0][info]
			pass
		else:
			pass
		pass
	
	
	for idict in range(1, nHistInCat):
		# * Get histogram info
		name_hist  = "{}_{}" . format (list_histByCat[idict]["histogram"], regECAL)
		title_hist = "{} ({})" . format (list_histByCat[idict]["titleX"], regECAL.replace("_","-"))
		name_var   = "{}" . format (list_histByCat[idict]["variable"])
		nBins      = int(list_histByCat[idict]["nBins"])
		binMin     = float(list_histByCat[idict]["binMin"])
		binMax     = float(list_histByCat[idict]["binMax"])
		
		histList[name_hist] = dataFrameHist.Histo1D ((name_hist, title_hist, nBins, binMin,  binMax),  name_var, "ev_weight")
		histList[name_hist] . Sumw2()
		histList[name_hist] . SetDirectory(0)
		
		#print ("     ||    |     [*] Direct integral from [ {} ]: {}" . format(name_hist, histList[name_hist].Integral()))
		pass
	
	pass










# + Merge the histograms
#=======================
def Merge_Histogram (dict_listHist):
	nHist = len(dict_listHist["pathHist"])
	
	merger = ROOT.TFileMerger ()
	
	for ihist in range(nHist-1):
		path_hist = "{}" . format (dict_listHist["pathHist"][ihist])
		print ("     ||   |--> Adding to merger: [{}]".format(path_hist))
		merger . AddFile (path_hist, False)
		pass
	
	path_histtarget = "{}" . format (dict_listHist["pathHist"][nHist-1])
	print ("     ||   |--> Output is set to: [{}]".format(path_histtarget))
	merger . OutputFile (path_histtarget, "recreate")
	
	merger . Merge()
	
	pass



######end of the function  
