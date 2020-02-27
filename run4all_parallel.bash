# last modified  Thu Feb 27 15:33:17 -03 2020
markerlist=`seq 5 5 25`

EQdatafile="catalogBrazil_chronological_1800-2019_excludeotherCountries.csv" # ordered from oldest to youngest
npointstotal=`wc -l $EQdatafile | awk '{print $1-2}'`  # because remove 1 for the header + remove other for the python index (0... npoints) 
PYTHONSCRIPT="plotearthquake_BR.py"
points=`seq 1 1 $npointstotal` 

# args for parallelizing:
NCORES=3 # you can change this, but ideally thois should be the number of processors
NPROC=0
# caveat, I am not sure if this is truly parallel!!
for point in $points
do
    for marker in $markerlist
    do
        # parallel run:
        parallel_run(){
            # run it biatch!
            echo python $PYTHONSCRIPT -markersize $marker -npoints $point -usgsdata $EQdatafile   
            python $PYTHONSCRIPT -markersize $marker -npoints $point -usgsdata $EQdatafile   
            echo ran: Point ${point}, marker ${marker} out of total points: ${npointstotal}   
            }
        
        parallel_run &
        NPROC=$(($NPROC+1))
        if [ "$NPROC" -ge "$NCORES" ]; then
            wait
             NPROC=0
        fi
    done
    wait # clear out last processes before moving on
done


