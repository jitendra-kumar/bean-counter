# Author: Jitendra (Jitu) Kumar
# Oak Ridge National Laboratory

# This routine queries Google Scholar using scholar ID and creates plots
# of publications and citations per year. Google Scholar entried are
# often not clean with unwanted conference abstracts etc. included so
# there also is an option to read bibtex files to get publication
# statistics.
# Publications statistics are plotted as pile of beans, because let's
# face it fellow academics, bean counting is all this is. But you can
# turn "the beans" that off and use just histograms if choose so.

# Three odd prerequisites - svgpath2mpl pybtex scholarly that can be
# installed via pip
#!pip install svgpath2mpl pybtex
#!pip install git+https://github.com/scholarly-python-package/scholarly.git

import argparse
from pybtex.database.input import bibtex
from svgpath2mpl import parse_path
import matplotlib.pyplot as plt      
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd 
from scholarly import scholarly 
from datetime import date
##############################################################################
############### CREATE MATPLOTLIB PATHS FOR BEAN #############################
##############################################################################
bean = parse_path("""
		    M498.915,156.87c-13.95-28.684-38.087-47.156-69.797-53.417c-57.873-11.43-86.542,7.008-111.835,23.278
			c-18.19,11.701-33.895,21.805-61.264,21.805c-0.012,0-0.023,0-0.037,0c-27.359,0-43.07-10.106-61.259-21.807
			c-25.29-16.269-53.955-34.714-111.814-23.277c-31.728,6.263-55.875,24.742-69.829,53.441
			C-5.704,195.525-2.47,247.03,11.506,274.495c16.768,33.004,45.727,63.463,83.74,88.081
			c48.582,31.476,107.141,49.524,160.683,49.524c0.023,0,0.051,0,0.073,0c53.567-0.002,112.158-18.05,160.744-49.515
			c38.033-24.63,66.991-55.081,83.74-88.053C514.472,247.037,517.707,195.508,498.915,156.87z M470.724,259.406
			c-13.887,27.339-39.501,54.031-72.125,75.157c-43.328,28.059-95.305,44.151-142.604,44.151h-0.006c-0.023,0-0.041,0-0.065,0
			c-47.266,0-99.213-16.093-142.531-44.158c-32.608-21.118-58.222-47.818-72.129-75.192c-8.547-16.794-12.808-57.749,1.838-87.871
			c9.335-19.196,24.901-31.068,46.274-35.287c10.209-2.018,19.11-2.909,27.052-2.909c26.791,0,42.587,10.158,60.232,21.511
			c19.757,12.71,42.148,27.116,79.315,27.115c0.012-0.001,0.03,0,0.048,0c37.171,0,59.564-14.404,79.32-27.113
			c22.877-14.718,42.637-27.428,87.304-18.603c21.354,4.217,36.911,16.082,46.242,35.266
			C483.545,201.601,479.28,242.586,470.724,259.406z
			""")

filled_bean = parse_path("""
				m 241.4478,377.99098 c -12.82178,-1.33462 -20.2416,-2.30859 -27.02553,-3.54755 C 147.40195,362.20339 82.595184,322.39847 
				50.00616,273.45752 40.368185,258.98358 36.685724,249.18592 34.739613,232.83891 31.485944,205.50863 37.284038,178.0068 
				49.87659,161.04038 c 13.831166,-18.63525 34.635181,-27.09596 66.54104,-27.06132 12.88633,0.014 18.87496,0.94338 
				28.91934,4.48808 9.107,3.2139 15.23319,6.59853 38.40391,21.2176 25.52693,16.10567 45.59295,22.29761 72.25912,22.29761 
				28.60313,0 46.93791,-6.13466 78.7007,-26.33258 23.53662,-14.96692 34.05874,-19.44276 50.43814,-21.45508 10.70174,-1.31478 
				29.43691,0.1712 41.62682,3.30164 25.65216,6.58762 42.97607,26.35181 48.94553,55.8401 4.05385,20.02548 2.93782,43.20276 
				-2.8868,59.95233 -4.11322,11.82815 -16.98413,30.54028 -31.20954,45.3734 -39.54002,41.22915 -97.43319,69.83948 
				-157.69838,77.93323 -6.75329,0.90699 -13.32154,1.29061 -24.64965,1.43967 -8.49373,0.11178 -16.5123,0.0919 -17.81902,-0.0441 
				z m 36.35008,-121.71132 c 3.85525,-0.49954 9.6824,-1.54798 12.94922,-2.32985 9.78513,-2.34194 25.23678,-7.8984 25.24787,-9.07921 
				0.002,-0.24913 -2.98506,-7.22073 -6.63867,-15.49246 -5.19853,-11.76937 -6.84611,-14.97429 -7.57735,-14.73963 -0.51392,0.16492 
				-4.35045,1.51676 -8.52562,3.0041 -11.48321,4.09069 -17.99591,5.303 -28.6408,5.33136 -7.27891,0.0194 -9.86628,-0.21675 
				-14.13723,-1.29025 -5.92962,-1.4904 -12.3807,-4.30615 -17.01321,-7.42587 l -3.15333,-2.12357 -1.29564,1.58947 c -6.3663,7.81008 
				-19.33891,25.17058 -19.09889,25.55893 0.68352,1.10596 9.23645,6.41764 14.55559,9.03955 8.53524,4.20718 19.6792,7.43825 
				29.15431,8.45296 5.40184,0.57849 17.8551,0.32322 24.17375,-0.49553 z
   """)
##############################################################################


##############################################################################
### Parse bibtex files and get counts per year 
##############################################################################
def get_bibcounts(biblist):
	bibdata=pd.read_csv(biblist, delimiter=" ")
	bibdata['count'] = "count"
	# loop over all bibfiles and let's count the number of entries
	for b in range(bibdata.shape[0]):
		parser = bibtex.Parser()
		bib_data = parser.parse_file(bibdata['bibfilename'][b])
		bibdata['count'][b] = len(bib_data.entries.keys())
		print("%d num bibs %d"%(bibdata['year'][b], len(bib_data.entries.keys())))
	print(bibdata)
	return(bibdata)
##############################################################################


##############################################################################
## Plot publications per year time series
##############################################################################
def plot_bibcounts(bibdata, cumulative, style):
	print("Executed")
	if cumulative:
		# Plot cumulative counts over years
		print("Plotting cumulative pubs time series")

		# make the bar plots
		if style=='bars':
			print("Plotting pubs cumulative time series as bars")
			with plt.xkcd():
				cum=0
				cumcount=np.zeros((bibdata['year'].shape[0]), int)
				for y in range(bibdata['year'].shape[0]):
					cumcount[y]=cum+bibdata['count'][y]
				bibdata['cumcount']=cumcount
				fig = plt.figure(figsize=[10,6]) #, dpi=300)
				ax = fig.add_subplot(111)
				ax.xaxis.set_major_locator(MaxNLocator(integer=True))
				ax.set_xticks(np.arange(bibdata['year'].min(), bibdata['year'].max(), step=2))
				plt.bar(bibdata['year'], bibdata['cumcount'])
				ax.set_ylabel("# Publications")
				ax.set_xlabel("Year")
				ax.set_title("Peer-Reviewed Publications Over Years")
				fig.autofmt_xdate()
				plt.savefig("bib_pubs_overyears.png", dpi=300)
		# else default would be bean plots
		else:
			print("Plotting pubs cumulative time series as beans")
			with plt.xkcd():
				fig = plt.figure(figsize=[10,4]) #, dpi=300)
				ax = fig.add_subplot(111)
				cum=0
				for b in range(bibdata.shape[0]):
					cum = cum + bibdata['count'][b]
					points = np.zeros((cum, 2), int)
					points[:,0] = bibdata['year'][b]
					points[:,1] = [i for i in range(1, cum+1)]
					ax.scatter(points[:,0], points[:,1], marker=filled_bean, s=500,
							color='darkolivegreen') #, fillstyle='full', markerfacecolor='darkolivegreen')
				ax.set_ylim(0, bibdata['count'].sum()+5)
				ax.xaxis.set_major_locator(MaxNLocator(integer=True))
				ax.set_xticks(np.arange(bibdata['year'].min(), bibdata['year'].max(), step=2))
				ax.set_xlabel("Year")
				ax.set_ylabel("# Publications")
				ax.set_title("Peer-Reviewed Publications Over Years")
				plt.savefig("bib_pubs_overyears.png", dpi=300)


	else:
		# Plot individual years
		print("Plotting pubs time series")

		# make the bar plots
		if style=='bars':
			print("Plotting pubs time series as bars")
			with plt.xkcd():
				fig = plt.figure(figsize=[10,6]) #, dpi=300)
				ax = fig.add_subplot(111)
				ax.xaxis.set_major_locator(MaxNLocator(integer=True))
				ax.set_xticks(np.arange(bibdata['year'].min(), bibdata['year'].max()), 2)
				plt.bar(bibdata['year'], bibdata['count'])
				ax.set_ylabel("# Publications")
				ax.set_xlabel("Year")
				ax.set_title("Peer-Reviewed Publications Per Year")
				fig.autofmt_xdate()
				plt.savefig("bib_pubs_peryear.png", dpi=300)

		# else default would be bean plots
		else:
			print("Plotting pubs time series as beans")
			with plt.xkcd():
				#fig = plt.figure()	
				fig = plt.figure(figsize=[10,4]) #, dpi=300)
				ax = fig.add_subplot(111)
				for b in range(bibdata.shape[0]):
					points = np.zeros((bibdata['count'][b],2), int)
					points[:,0] = bibdata['year'][b]
					points[:,1] = [i for i in range(1, bibdata['count'][b]+1)]
		
					ax.scatter(points[:,0], points[:,1], marker=filled_bean, s=2000,
							color='darkolivegreen') #, fillstyle='full', markerfacecolor='darkolivegreen')
				ax.set_ylim(0, bibdata['count'].max()+2)
				ax.xaxis.set_major_locator(MaxNLocator(integer=True))
				ax.set_xticks(np.arange(bibdata['year'].min(), bibdata['year'].max()), 2)
				ax.set_xlabel("Year")
				ax.set_ylabel("# Publications")
				ax.set_title("Peer-Reviewed Publications Per Year")
				#plt.show()
				plt.savefig("bib_pubs_peryear.png", dpi=300)

##############################################################################

##############################################################################
## Plot citations per year time series based on data from Google Scholar
##############################################################################
def gs_plot_citations_ts(gs_citations_data, name, hindex):
	# Plot individual years
	print("Plotting GS citation time series")

	with plt.xkcd():
		#fig = plt.figure()	
		fig = plt.figure(figsize=[10,6]) #, dpi=300)
		ax = fig.add_subplot(111)
		#ax.set_ylim(0, bibdata['count'].max()+2)
		#ax.set_xlabel("Year")
		#ax.xaxis.set_major_locator(mdates.YearLocator())
		#ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
		ax.xaxis.set_major_locator(MaxNLocator(integer=True))
		ax.set_xlim(min(gs_citations_data.index), max(gs_citations_data.index)+1)
		print(min(gs_citations_data.index), max(gs_citations_data.index))
		print(np.arange(min(gs_citations_data.index), max(gs_citations_data.index)))
		ax.set_xticks(np.arange(min(gs_citations_data.index), max(gs_citations_data.index), step=2))
		plt.bar(gs_citations_data.index, gs_citations_data['citations'])
		ax.set_ylabel("# Citations")
		ax.set_xlabel("Year")
		ax.set_title("Citations Per Year (based on Google Scholar data) \n Author: %s hindex: %d (updated: %s)"%(name, hindex, date.today().strftime("%m/%d/%Y")))
		#plt.show()
		fig.autofmt_xdate()
		plt.savefig("gs_citations_peryear.png", dpi=300)

##############################################################################
def gs_plot_pubs_ts(gs_citations_data, name, hindex, bibdata, style):
	# Plot individual years
	print("Plotting GS pubs time series")

	# make the bar plots
	if style=='bars':
		print("Plotting pubs time series as bars")
		with plt.xkcd():
			fig = plt.figure(figsize=[10,6]) #, dpi=300)
			ax = fig.add_subplot(111)
			ax.xaxis.set_major_locator(MaxNLocator(integer=True))
			ax.set_xlim(min(gs_citations_data.index), max(gs_citations_data.index)+1)
			ax.set_xticks(np.arange(min(gs_citations_data.index), max(gs_citations_data.index)), 2)
			plt.bar(bibdata['year'], bibdata['count'])
			ax.set_ylabel("# Publications")
			ax.set_xlabel("Year")
			ax.set_title("Publications Per Year (based on Google Scholar data) \n Author: %s hindex: %d (updated: %s)"%(name, hindex, date.today().strftime("%m/%d/%Y")))
			fig.autofmt_xdate()
			plt.savefig("gs_pubs_peryear_bars.png", dpi=300)
	# else default would be bean plots
	else:
		print("Plotting pubs time series as beans")
		with plt.xkcd():
			fig = plt.figure(figsize=[10,6]) #, dpi=300)
			ax = fig.add_subplot(111)
			for b in range(bibdata.shape[0]):
				points = np.zeros((bibdata['count'][b],2), int)
				points[:,0] = bibdata['year'][b]
				points[:,1] = [i for i in range(1, bibdata['count'][b]+1)]
	
				ax.scatter(points[:,0], points[:,1], marker=filled_bean, s=2000,
						color='darkolivegreen') #, fillstyle='full', markerfacecolor='darkolivegreen')
#			ax.set_ylim(0, bibdata['count'].max()+2)
			ax.xaxis.set_major_locator(MaxNLocator(integer=True))
			ax.set_xticks(np.arange(bibdata['year'].min(), bibdata['year'].max()+1, step=2))
			ax.set_xlabel("Year")
			ax.set_ylim(0, bibdata['count'].max()+2)
			ax.set_ylabel("# Publications")
			ax.set_title("Publications Per Year (based on Google Scholar data) \n Author: %s hindex: %d (updated: %s)"%(name, hindex, date.today().strftime("%m/%d/%Y")))
			plt.savefig("gs_pubs_peryear_beans.png", dpi=300)

##############################################################################



##############################################################################
## Main function
##############################################################################
if __name__ == "__main__":
	desc = """
					Routine to parse bibtex files and plot pubs time series.
				  """
	parser = argparse.ArgumentParser(description=desc)
	parser.add_argument('-b', '--biblist', dest='biblist', type=str, action='store', default=None,
	                    help='name of file containing bibtex list. Space seperated two columns [year bibtexfilename]')
	parser.add_argument('-c', '--cumulative', dest="cumulative", default=False, 
			action='store_true', help='plot cumulative time series')
	parser.add_argument('--gscitations', dest="plot_citations", default=False, 
			action='store_true', help='plot Google Scholar citations time series')
	parser.add_argument('--gspubs', dest="plot_pubs", default=False, 
			action='store_true', help='plot Google Scholar publications time series')
	parser.add_argument('--authorid', dest="gauthorid", type=str,# default=None, 
			action='store', help='Google Scholar author id')
	parser.add_argument('--style', dest="style", default='beans', type=str, 
			action='store', help='plot as bars or beans. Default are bean, because it is!')
	# Execute the parse_args() method
	args = parser.parse_args()
	
	# Check for authorid if citations flag provided 
	if (args.plot_citations == True) and (args.gauthorid == None):
		printf("Google Scholar author id must be provided with --authorid flag when --gscitations is used.")
		exit(1)


	if args.biblist != None:	
		####################################################################
		############ Extract and plot data from bibtex files ###############
		####################################################################
		# get yearly bibcounts based on the biblist
		year_bibcounts = get_bibcounts(args.biblist)
	
		# Plot the bib counts
		print("make the plot")	
		plot_bibcounts(year_bibcounts, args.cumulative, args.style)

	if args.plot_citations == True:
		####################################################################
		####### Extract and plot data from Google Scholar profile ##########
		####################################################################
		# Retrieve information from Google Scholar 
		# https://pypi.org/project/scholarly/ 
		author = scholarly.search_author_id(args.gauthorid)
		scholarly.pprint(author)
		scholarly.pprint(scholarly.fill(author, sections=['basics', 'indices', 'coauthors', 'counts', 'publications']))
		scholarly.fill(author, sections=[]) #'basics', 'indices', 'counts'])
		plist=[]
		for a in author['publications']:
#			print(a['bib']['pub_year'])
			try:	
				plist.append(a['bib']['pub_year'])
			except:
				print('Pub in GScholar without year')
		years,counts=np.unique(plist, return_counts=True)
		print(years)
		bibdata=pd.DataFrame(years.astype(int), columns=['year'], dtype=int)
		bibdata['count']=counts
		gs_citations_data = pd.DataFrame.from_dict(author['cites_per_year'], columns=['citations'], orient='index', dtype=int)
		print(gs_citations_data)
		name = author['name']
		hindex = author['hindex']
	
		# plot citations per year
		gs_plot_citations_ts(gs_citations_data, name, hindex)
		# plot pubs per year
		gs_plot_pubs_ts(gs_citations_data, name, hindex, bibdata, args.style)

##############################################################################
