import sys
import math
import shutil
import time

import os
from os import listdir
from os.path import isfile, isdir, join

import ROOT as myroot
from ROOT import gStyle
from ROOT import gROOT

import Lib_Python.tool_InfoCollector as collector




# + Global value
#===============
percentDist = 0.70
percentRate = 0.30

ratioPad = (percentDist/percentRate)





# + Visualization setup for distribution histogram
#=================================================
def Characterize_histDist (hist, colour_fill, style_fill, colour_mark, style_mark, nameXaxis):
	# + Global visual setting
	#------------------------
	hist . SetTitle ("")
	hist . SetLineColor (colour_mark)
	hist . SetLineWidth (1)
	hist . SetMarkerColor (colour_mark)
	hist . SetMarkerStyle (style_mark)
	hist . SetMarkerSize (0.75)
	hist . SetFillColor (colour_fill)
	hist . SetFillStyle (style_fill)
	
	
	# + Get the title for Y axis
	#---------------------------
	nameYaxis = ""
	widthBinX = float((hist.GetXaxis().GetXmax() - hist.GetXaxis().GetXmin()) / hist.GetNbinsX())
	tmp = widthBinX
	
	nPow = 0
	while (tmp < 1.0):
		tmp *= 10
		nPow += 1
		pass
	
	widthBinX = round (widthBinX, nPow)
	unitY = ""
	
	if "GeV" in nameXaxis:
		unitY = " GeV"
		pass
	if "rad" in nameYaxis:
		unitY = " rad"
		pass
	
	nameYaxis = "#Event/{}{:s}" . format (widthBinX, unitY)
	
	
	# + Axes settings
	#----------------
	hist . GetXaxis() . SetTitle       ("")
	hist . GetXaxis() . SetTitleFont   (42)
	hist . GetXaxis() . SetTitleSize   (0.0)
	hist . GetXaxis() . SetTitleOffset (0.4)
	hist . GetXaxis() . SetLabelSize   (0.0)
	hist . GetXaxis() . SetLabelOffset (0.0)
	
	hist . GetYaxis() . SetTitle       (nameYaxis)
	hist . GetYaxis() . SetMaxDigits   (4)
	hist . GetYaxis() . SetTitleFont   (42)
	hist . GetYaxis() . SetTitleSize   (0.055)
	hist . GetYaxis() . SetTitleOffset (0.480*ratioPad)
	hist . GetYaxis() . SetLabelSize   (0.045)
	hist . GetYaxis() . SetLabelOffset (0.003)
	
	pass





# + Visualization setup for ratio histogram
#==========================================
def Characterize_histRatio (hist, colour_fill, style_fill, colour_mark, style_mark, nameXaxis, nameYaxis):
	# + Global visual setting
	#------------------------
	hist . SetTitle ("")
	hist . SetLineColor (colour_mark)
	hist . SetLineWidth (1)
	hist . SetMarkerColor (colour_mark)
	hist . SetMarkerStyle (style_mark)
	hist . SetMarkerSize (0.75)
	hist . SetFillColor (colour_fill)
	hist . SetFillStyle (style_fill)
	
	
	# + Axes settings
	#----------------
	hist . GetXaxis() . SetTitle       (nameXaxis)
	hist . GetXaxis() . SetTitleFont   (42)
	hist . GetXaxis() . SetTitleSize   (0.055*ratioPad)
	hist . GetXaxis() . SetTitleOffset (0.900)
	hist . GetXaxis() . SetLabelSize   (0.045*ratioPad)
	hist . GetXaxis() . SetLabelOffset (0.007*ratioPad)
	
	hist . GetYaxis() . SetTitle       (nameYaxis)
	hist . GetYaxis() . SetTitleFont   (42)
	hist . GetYaxis() . SetTitleSize   (0.055*ratioPad)
	hist . GetYaxis() . SetTitleOffset (0.480)
	hist . GetYaxis() . SetLabelSize   (0.045*ratioPad)
	hist . GetYaxis() . SetLabelOffset (0.003*ratioPad)
	hist . GetYaxis() . SetNdivisions  (505)
	hist . GetYaxis() . SetRangeUser   (-0.2, 2.2)
	
	pass





# + Get the ratio histogram
#==========================
def Get_histRatio (hist_tar, hist_ref):
	hist_ratio = hist_tar . Clone()
	hist_ratio . Divide(hist_tar, hist_ref)
	
	return hist_ratio






# + Main script to create plots
#==============================
def Create_Plot (dict_plotBlock):
	myroot.gErrorIgnoreLevel = myroot.kError
	myroot.gErrorIgnoreLevel += myroot.kBreak
	myroot.gErrorIgnoreLevel += myroot.kSysError
	myroot.gErrorIgnoreLevel += myroot.kFatal
	
	myroot . gStyle . SetOptStat (0)
	
	
	
	
	# + Loop over the input histograms to create plots
	#-------------------------------------------------
	nHist = len(dict_plotBlock["pathTar"])
	
	for ihist in range(nHist):
		print ("     ||")
		print ("     || $$ Working on the {:02d}th pair of histograms ..." . format (ihist+1))
		# + Get the basic info
		#---------------------
		path_histTar = dict_plotBlock["pathTar"][ihist]
		isMC_tar     = dict_plotBlock["isMCTar"][ihist]
		lumi_tar     = dict_plotBlock["lumiTar"][ihist]
		leg_tar      = dict_plotBlock["legTar"][ihist]
		year_tar     = dict_plotBlock["yearTar"][ihist]
		
		path_histRef = dict_plotBlock["pathRef"][ihist]
		isMC_ref     = dict_plotBlock["isMCRef"][ihist]
		lumi_ref     = dict_plotBlock["lumiRef"][ihist]
		leg_ref      = dict_plotBlock["legRef"][ihist]
		year_ref     = dict_plotBlock["yearRef"][ihist]
		
		name_ratio = dict_plotBlock["nameRatio"][ihist]
		dir_plot   = dict_plotBlock["dirPlot"][ihist]
		path_plot  = dict_plotBlock["pathPlot"][ihist]
		
		
		
		
		
		# + Open root file to read histogram
		#-----------------------------------
		file_histTar = myroot.TFile . Open (path_histTar)
		file_histRef = myroot.TFile . Open (path_histRef)
		
		list_nameHist = collector . Get_listHist (file_histTar, "TH1D")
		
		for name_hist in list_nameHist:
			#print ("     ||    [+]  Histogram name: {}" . format(name_hist))
			
			# + Get histogram from file
			#--------------------------
			# * Read histogram
			hist_tar = file_histTar . Get(name_hist)
			hist_refVal = file_histRef . Get(name_hist)
			hist_refErr = hist_refVal . Clone()
			
			# * Remove the binding to files
			hist_tar . SetDirectory (0)
			hist_refVal . SetDirectory (0)
			hist_refErr . SetDirectory (0)
			
			nameXaxis = hist_tar.GetTitle()
			
			# * Scale histogram if required
			normFactor = 1.0
			intTar = hist_tar.Integral()
			intRef = hist_refVal.Integral()
			
			if intTar!=0 and intRef!=0:
				normFactor = intTar/intRef
				pass
			
			#print ("     ||    [+]  Normalizing factor is: {}".format(normFactor))
			
			if (normFactor < 1.0):
				#print ("     ||         |> Normalizing reference by: {}".format(normFactor))
				hist_refErr . Scale (normFactor)
				hist_refVal . Scale (normFactor)
				pass
			else:
				#print ("     ||         |> Normalizing target by: {}".format(1/normFactor))
				hist_tar . Scale (1/normFactor)
				pass
			
			
			
			
			# + Get ratio histogram
			#----------------------
			hist_ratVal = Get_histRatio (hist_tar, hist_refVal)
			hist_ratErr = hist_refVal . Clone()
			
			for ibin in range(hist_ratErr.GetNbinsX()):
				bin_orgErr = hist_ratErr.GetBinError(ibin+1)
				bin_orgCon = hist_ratErr.GetBinContent(ibin+1)
				
				bin_newErr = 0.0
				bin_newCon = 1.0
				
				if bin_orgCon > 0:
					bin_newErr = bin_orgErr/bin_orgCon
					pass
				
				hist_ratErr . SetBinContent (ibin+1, bin_newCon)
				hist_ratErr . SetBinError   (ibin+1, bin_newErr)
				
				pass
			
			
			
			# + Characterize histogram
			#-------------------------
			Characterize_histDist (hist_tar,    myroot.kBlack,    1001, myroot.kBlack,    20, nameXaxis)
			Characterize_histDist (hist_refVal, myroot.kOrange-4, 1001, myroot.kOrange-4,  1, nameXaxis)
			Characterize_histDist (hist_refErr, myroot.kOrange+7, 3144, myroot.kOrange+7,  1, nameXaxis)
			
			Characterize_histRatio (hist_ratVal, myroot.kBlack,    1001, myroot.kBlack,    20, nameXaxis, name_ratio)
			Characterize_histRatio (hist_ratErr, myroot.kOrange+7, 3144, myroot.kOrange+7,  1, nameXaxis, name_ratio)
			
			
			
			# + Draw histogram
			#-----------------
			for isLog in range(2):
				#print ("     ||    [+]  Creating log scale: {}" . format(bool(isLog)))
				# + Set maximum Y
				#----------------
				heightMax = max (hist_tar.GetMaximum(), hist_refVal.GetMaximum())
				heightMin = max (hist_tar.GetMaximum(), hist_refVal.GetMaximum())
				multFactor = 1.0
				
				if (intTar!=0) and (intRef!=0):
					if "rad" in nameXaxis:
						multFactor = pow(10, 0.9*(math.log10(heightMax)-math.log10(heightMin))) if (isLog) else 1.8
						pass
					else:
						multFactor = pow(10, 0.9*(math.log10(heightMax)-math.log10(heightMin))) if (isLog) else 1.5
						pass
					pass
				
				hist_tar    . SetMaximum (heightMax*multFactor)
				hist_refVal . SetMaximum (heightMax*multFactor)
				hist_refErr . SetMaximum (heightMax*multFactor)
				
				
				
				# + Create canvas
				#----------------
				# * Canvas
				canvas = myroot.TCanvas ("canvas", "", 600, 600)
				
				# * Pad for distribution
				canvas . cd()
				pad1 = myroot.TPad ("pad1", "", 0.0, 0.3, 1.0, 1.0)
				pad1 . SetLeftMargin   (0.13)
				pad1 . SetRightMargin  (0.05)
				pad1 . SetTopMargin    (0.08)
				pad1 . SetBottomMargin (0.02)
				pad1 . SetTicks (1, 1)
				pad1 . SetLogy  (isLog)
				pad1 . Draw()
				pad1 . cd()
				
				# * Draw histogram for distribution
				hist_refVal . Draw("hist")
				hist_refErr . Draw("same e2")
				hist_tar    . Draw("same ep")
				
				# * Draw legend
				legend = myroot.TLegend (0.62, 0.65, 0.91, 0.89)
				legend . SetTextFont (42)
				legend . SetTextSize (0.055)
				legend . SetFillColorAlpha (0, 0.75)
				legend . SetLineColorAlpha (0, 0.75)
				legend . AddEntry (hist_tar,    "{}".format(leg_tar), "ep")
				legend . AddEntry (hist_refVal, "{}".format(leg_ref),  "f")
				legend . AddEntry (hist_refErr, "Norm.Unc",            "f")
				legend . Draw ("same")
				
				texLogo = myroot.TLatex()
				texLogo . SetNDC()
				texLogo . SetTextFont (42)
				texLogo . SetTextSize (0.07)
				texLogo . DrawLatex (0.18, 0.82, "#bf{CMS}")
				
				str_lumi = ""
				if (year_ref != year_tar):
					str_lumi = "{:.2f} fb^{{-1}} {} vs {:.2f} fb^{{-1}} {} (13 TeV)" . format (lumi_tar, year_tar, lumi_ref, year_ref)
					pass
				else:
					if (lumi_tar != lumi_ref):
						str_lumi = "{:.2f} fb^{{-1}} vs {:.2f} fb^{{-1}} {} (13 TeV)" . format (lumi_tar, lumi_ref, year_ref)
						pass
					else:
						str_lumi = "{:.2f} fb^{{-1}} {} (13 TeV)" . format (lumi_ref, year_ref)
						pass
					pass
				
				texLumi = myroot.TLatex()
				texLumi . SetNDC()
				texLumi . SetTextFont (42)
				texLumi . SetTextSize (0.055)
				texLumi . SetTextAlign (31)
				texLumi . DrawLatex (0.955, 0.935, "{}".format(str_lumi))
				
				# * pad for ratio
				canvas . cd()
				pad2 = myroot.TPad ("pad2", "", 0.0, 0.0, 1.0, 0.3)
				pad2 . SetLeftMargin   (0.13)
				pad2 . SetRightMargin  (0.05)
				pad2 . SetTopMargin    (0.01)
				pad2 . SetBottomMargin (0.30)
				pad2 . SetTicks (1, 1)
				pad2 . SetGrid  (0, 1)
				pad2 . Draw()
				pad2 . cd()
				
				hist_ratErr . Draw ("e2")
				hist_ratVal . Draw ("ep same")
				
				pad2 . Update()
				
				
				
				# + Save the plots
				#-----------------
				str_plotOut = path_plot
				dir_plot_check = ""
				
				if (isLog):
					str_plotOut = str_plotOut . replace ("/plot", "/Scale_Log/plot")
					dir_plot_check = dir_plot + "/Scale_Log/"
					pass
				else:
					str_plotOut = str_plotOut . replace ("/plot", "/Scale_Linear/plot")
					dir_plot_check = dir_plot + "/Scale_Linear/"
					pass
				
				# Create directory to plots
				if not os.path.exists(dir_plot_check):
					#print ("     ||         | >> Creating [{}]" . format(dir_plot_check))
					os.makedirs (dir_plot_check)
					pass
				
				str_plotOut = str_plotOut . replace ("*", name_hist)
				canvas . SaveAs (str_plotOut)
				
				str_plotOut = str_plotOut . replace (".png", ".pdf")
				canvas . SaveAs (str_plotOut)
				
				str_plotOut = str_plotOut . replace (".pdf", ".C")
				canvas . SaveAs (str_plotOut)
				
				str_plotOut = str_plotOut . replace (".C", ".{png,pdf,C}")
				print ("     ||         | > Plot saved to: {}" . format(str_plotOut))
				
				pass
			
			pass
		
		pass
	
	pass
