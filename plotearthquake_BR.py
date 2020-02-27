''' Plots selected earthquake data on the map
    hardwired inside this script are:
    1. map boundaries
    2. page size for the map
    3. city names to highlight
'''

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import gmplot


class EarthquakeData(object):
    ''' Class storing & manipulating earthquake data '''

    def __init__(self):
        self.latitude = []
        self.longitude = []
        self.minLatitude = 0.0
        self.maxLatitude = 0.0
        self.minLongitude = 0.0
        self.maxLongitude = 0.0
        self.midLatitude = 0.0
        self.midLongitude = 0.0
        self.date = ''
        self.magnitude = 0.0
        self.map = Basemap() 
    
    def ReadAndGetData(self, filename):
        ''' 
        Reads the data file and filters as necessary 
        (e.g. only accept earthquakes with magnitude greater than 5 etc)
        '''

        # Use pandas to get the USGS data content
        df = pd.read_csv(filename)  # e.g. filename:  USGS_americas_1950_2017_over6.csv

        # Use hardcoded min/max Longitude/Latitude for the specific map output
        # One can also use other min/max values (up to the user)
        self.minLongitude, self.maxLongitude = (-74.963208, -33.333960)  # custom brazil
        self.minLatitude, self.maxLatitude = (-35.080177,  5.901722 )   # custom brazil
        
        # Filter data & get only those larget than X magnitude
        #minMagnitudeDesired = 5.0  # too big of minMag, for Brazil, it needs to be lower
        minMagnitudeDesired = 0.50
        
        # markercolors...
        refdate = pd.Timestamp('1920-01-01') # hardwired limit for "historical EQs", still needs to be comkplemented by older catalog 
        df['markercolor'] = np.where(pd.to_datetime(df['time']) <= refdate,'blue','red') # to later assign colors depending on the date
        df['colornumrgb'] = np.where(pd.to_datetime(df['time']) <= refdate,'2','0') # rgb =1 2 3 (cuirrently not used) 
        filteredDf = df[(df['latitude'] >= self.minLatitude) & 
                        (df['latitude'] <= self.maxLatitude) &
                        (df['longitude'] >= self.minLongitude - 3.4) &
                        (df['longitude'] <= self.maxLongitude - 0.7) &
                        (df['mag'] >= minMagnitudeDesired) ]  # original 
                        #(df['mag'] >= minMagnitudeDesired) &
                        #(~df.place.str.contains('Chile') )]   # the "~" is like the NOT, so it will say like it does not contain that string 
        # update: I had to do the excluding manually with grep -v because the npoints were not the filtered npoints... so I got lazy and did
        # it with grep to get the csv file... It can be fixed of course, but I'm lazy AF.
        
        filteredDf = df # Ignoring filters for now 
        #df = filteredDf

        # Filtered data is in panda dataframe format, use df.values.tolist() to convert to list  
        self.latitude    = (filteredDf.latitude).values.tolist()
        self.longitude   = (filteredDf.longitude).values.tolist()
        self.date        = (filteredDf.time).values.tolist()
        self.magnitude   = (filteredDf.mag).values.tolist()
        self.markercolor = (filteredDf.markercolor).values.tolist()
        self.colornumrgb = (filteredDf.colornumrgb).values.tolist()
        # If you don't want filtering, then min/max can be obtained from the read data
        #self.minLongitude = min(self.longitude)
        #self.maxLongitude = max(self.longitude)
        #self.minLatitude = min(self.latitude)
        #self.maxLatitude = max(self.latitude)

        # Calculate mid-point for longitudes and latitudes to center the map:
        self.midLatitude = 0.5*(self.maxLatitude + self.minLatitude)
        self.midLongitude = 0.5*(self.maxLongitude + self.minLongitude)
        # uncomment below to print the EQ info if you want
        #print "Quake info: \n", self.__str__()


    def DrawMap(self):
        ''' Draw the main background map where the earthquake data will be overlayed

        Some other options to check for: 
        self.map = Basemap(resolution='h', # c(crude), l(low), i)intermediate), h(high), f(full) or None
                    projection='merc', # 'ortho', 'gnom', 'mill'
                    lat_0=40.320373, lon_0=-74.43,
                    llcrnrlon=minLon, llcrnrlat= minLat, urcrnrlon=maxLon, urcrnrlat=maxLat )

         It is also possible to download arcgis images through the following command 
        elf.map.arcgisimage(service='World_Physical_Map', xpixels = 5000, verbose= False)
        '''

        fig, ax = plt.subplots(figsize=(8, 9)) #this is how big the figure will be. if you have extra white space, change this
        fig.patch.set_facecolor('white') # Set white background. I'm not racist, it just looks cool with the white BG

        self.map = Basemap(height=5e6, width=5.2e6,   # original:height=1.7e6, width=2.8e6
                  resolution='f', area_thresh=10., projection='omerc',   # check the projection
                  lon_0=self.midLongitude, lat_0=self.midLatitude, 
                  lon_1=self.minLongitude, lat_1=self.minLatitude, 
                  lon_2=self.maxLongitude, lat_2=self.maxLatitude)

        self.map.drawmapboundary(fill_color='#46bcec')
        self.map.fillcontinents(color='#f2f2f2', lake_color='#46bcec')
        self.map.drawcounties()
        self.map.drawcountries(linewidth=0.25)

        self.map.drawcoastlines()

        self.map.drawparallels(np.arange(self.minLatitude, self.maxLatitude, 10.))
        self.map.drawmeridians(np.arange(self.minLongitude, self.maxLongitude, 10.))

        plt.tight_layout()

        return 

    def PlotEarthquakeLocationsOnMap(self, bPlotPoints):
        ''' Plot epicenters '''
        
        if bPlotPoints:
            # Default size for already displayed points (in a time-lapse fashion, some points 
            # have already been displayed as shrinking points - at this stage only show shrunk versions)
            # to leave them with scaling according to the magnitude, I need to change this.... someday
            pstart = ARGS.npoints - ARGS.nsimpoints
            pend = ARGS.npoints
            
            #year    = pd.Timestamp( (self.date[ARGS.npoints].split('T'))[0] )  
            #refyear = pd.Timestamp('2019-04-01')
            #markeandrcolor = 'ro' # default marker and color: red circle
            
            #if year < refyear: # changes it for the older events
            #    markerandcolor = 'bo'
            #    print('historical EQ:',str(year),'symbol is changed to color blue. check script for details')

            x, y = self.map(self.longitude[0:pstart], self.latitude[0:pstart])
            #print('pstart=',pstart)
            # looping through events and their assigned color, I tried to 'do a cmap' to avoid the loop,
            # but for some reason basmap was not having it. still not sure why.
            for lon,lat,markcolor in zip(self.longitude[0:pstart], self.latitude[0:pstart], self.markercolor[0:pstart]):
                x, y = self.map(lon,lat)
                colorstring=markcolor
                self.map.plot(x, y, color=colorstring, marker='o', alpha=0.8, markersize=5, markeredgecolor='red',
                        fillstyle='full', markeredgewidth=0.1)

            # Custom (most of the time bigger) font for the new point to be displayed
            x, y = self.map(self.longitude[pstart:pend], self.latitude[pstart:pend])
            colorstring = str(self.markercolor[pstart:pend][0])
            
            self.map.plot(x, y, marker='o',color=colorstring , alpha=0.8, markersize=65-ARGS.markersize, markeredgecolor='red', 
                          fillstyle='full', markeredgewidth=0.1)

            day = (self.date[ARGS.npoints].split('T'))[0]
            print('date='+day)   
            magnitude = self.magnitude[pend]
            plt.title('Earthquake on {0} - magnitude {1:1.1f}'.format(day, magnitude))

        return


    def WriteCityNamesOnTheMap(self):
        ''' 
        Write names of selected cities on the map after finding 
        their corresponding latitude/longitude value
        '''
        # This part I brute-forced it, I just made a separate file and instead of reading it here, I copy-pasted
        # the values I need to make it smarter
        # Lat/lon coordinates of several cities that lie in the map of interest
        lats = [-23.550520,-22.906847,-3.106390,-3.718460,-8.055190,
                -12.977749,-15.779380,-25.428360]


        lons = [-46.633308,-43.172897,-60.026291,-38.541672,-34.871181,
                -38.501629,-47.925739,-49.27325]

        cities = ['Sao Paulo','Rio de Janeiro','Manaus','Fortaleza','Recife'
                ,'Salvador','Brasilia','Curitiba']  

        # Compute the native map projection coordinates for cities.
        xc, yc = self.map(lons, lats)

        # Plot filled circles at the locations of the cities.
        self.map.plot(xc[:-1], yc[:-1], 'go')

        # Some certain city names need to be shifted for better visualization
        # if there is a special place/city that you  want to highlight, the its here where you do it.
        # just change the fointsize and the names
        for name, xpt, ypt in zip(cities, xc, yc):
            if name == 'Sao Paulo' or name == 'Rio de Janeiro' or name == 'Brasilia' or name == 'Fortaleza':
                plt.text(xpt+10000, ypt-20000, name, fontsize=9)
            elif name == 'Chile':
                plt.text(xpt-40000, ypt-30000, name, fontsize=9)
            elif name == 'Bolivia':
                plt.text(xpt-30000, ypt+15000, name, fontsize=9)
            elif name == 'Peru' or name == 'Colombia':
                plt.text(xpt+20000, ypt-10000, name, fontsize=9)
            elif name == 'Ocean':
                plt.text(xpt+15000, ypt+10000, name, fontsize=11)
            else:
                plt.text(xpt+10000, ypt+10000, name, fontsize=9) # Default visualization

        return

    def UseGMPLOTtoDumptoGoogleMap(self, htmlfilename):
        ''' Convert the same earthquake data info to Google Map heat map format 
            NOTE: gmplot package needs to be pre-installed 

        # Some other options using gmplot
        gmap.plot(latitudes, longitudes, 'cornflowerblue', edge_width=10)
        gmap.plot(latitudes, longitudes, 'red', edge_width=8)
        gmap.scatter(more_lats, more_lngs, '#3B0B39', size=40, marker=False)
        gmap.scatter(marker_lats, marker_lngs, 'k', marker=True)
        gmap.scatter(lat, lon, 'r', size=10, marker=False)
        '''
        gmap = gmplot.GoogleMapPlotter(self.midLatitude, self.midLongitude, 3) # lat/lon/google map zoom level

        gmap.heatmap(self.latitude, self.longitude)

        gmap.draw(htmlfilename)

        return

    def SaveSnapshotsToFile(self, bSaveFigs=True, snapshotfilename='earthquakes_dpi240'):
        ''' 
        Save the earthquake snapshots in time to file
        Note that for (16,9) sized figure, dpi=120 gives (16,9)*120 =[1920,1080] pixels png file
        Similarly, dpi=240 gives (16,9)*240 =[3840,2160] pixels png file
        '''

        if bSaveFigs:
            OutFolder = 'Snapshots_{}'.format(ARGS.npoints - ARGS.npoints%100)
            if not os.path.exists(OutFolder):
                os.mkdir(OutFolder)

            outpngfilename = '{}/{}_{}_{}.png'.format(OutFolder, snapshotfilename,
                                                      ARGS.npoints, ARGS.markersize)
            plt.savefig(outpngfilename, facecolor='w', dpi=240) 
        else:
            plt.show()
            
        return


    def __str__(self):
        ''' Print some data on the earthquake class'''

        str1 = "Number of points = {}".format(len(self.longitude))
        str2 = "Latitude (min,max) = {}, {}".format(self.minLatitude, self.maxLatitude)
        str3 = "Longitude (min,max) = {}, {}".format(self.minLongitude, self.maxLongitude)
        str4 = "Mid points (Longitude, Langitude)= {}, {}".format(self.midLongitude, self.midLatitude)
       
        return '{}\n{}\n{}\n{}\n'.format(str1, str2, str3, str4)    


def ParseInput():
    ''' Parse input arguments '''

    parser = argparse.ArgumentParser()

    parser.add_argument("-markersize", type=float, default=5, help="Marker size to represent the earthquake data on the map")
    parser.add_argument("-npoints", type=int, default=1, help="Total number of points in the graph [sweep the whole range for final video output]")
    parser.add_argument("-nsimpoints", type=int, default=1, help="Number of simultaneous points having different marker size")
    parser.add_argument("-catalogdata", type=str, help="Filename (e.g. usgs.csv) that contains the earthquake data as downloaded from USGS or moho.iag.usp.br")

    args = parser.parse_args()

    return args


def main():

    quake = EarthquakeData();
    quake.ReadAndGetData(ARGS.catalogdata)

    quake.DrawMap()
    quake.WriteCityNamesOnTheMap()
    quake.PlotEarthquakeLocationsOnMap(True)
    quake.SaveSnapshotsToFile(True)

    # This is a bonus feature - dumping the earthquake heatmap to google maps format [uses gmplot]
    # could not make it work in all machines, so its commented for now
    #quake.UseGMPLOTtoDumptoGoogleMap("earthquake_test.html")


if __name__ == '__main__': # standard boilerplate calling main()
    ARGS = ParseInput()
    main()
