# last modified on Thu Feb 27 15:31:59 -03 2020
markerlist=`seq 5 5 25`
#markerlist='20'

EQdatafile="catalogBrazil_chronological_1800-2019_excludeotherCountries.csv" # ordered from oldest to youngest
npointstotal=`wc -l $EQdatafile | awk '{print $1-2}'`  # because remove 1 for the header + remove other for the python index (0... npoints) 
PYTHONSCRIPT="plotearthquake_BR.py"
points=`seq 1 1 $npointstotal` 

for point in $points
do
    for marker in $markerlist
    do
        # run it biotsch!
        echo python $PYTHONSCRIPT -markersize $marker -npoints $point -usgsdata $EQdatafile   
        python $PYTHONSCRIPT -markersize $marker -npoints $point -usgsdata $EQdatafile   
        echo ran: Point ${point}, marker ${marker} of total ${npointstotal}  
    done
done


