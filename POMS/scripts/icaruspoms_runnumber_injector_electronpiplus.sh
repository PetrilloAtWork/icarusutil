#!/bin/bash

#source.firstSubRun: 1
#Subrun follows $PROCESS+1
#After every 100 subruns, a new run is started
export NSUBRUNSPERRUN=100

while :; do
    case $1 in
        -h|-\?|--help)
            show_help    # Display a usage synopsis.
            exit
            ;;
        --fcl)       # Takes an option argument; ensure it has been specified.
            if [ "$2" ]; then
                FCL="$2"
                shift
            else
                echo "$0 ERROR: fcl requires a non-empty option argument."
                exit 1
            fi
            ;;
#        --file=?*)
#            file=${1#*=} # Delete everything up to "=" and assign the remainder.
#            ;;
#        --file=)         # Handle the case of an empty --file=
#            echo 'ERROR: "--file" requires a non-empty option argument.'
#            ;;
        -v|--verbose)
            verbose=$((verbose + 1))  # Each -v adds 1 to verbosity.
            ;;
        --)              # End of all options.
            shift
            break
            ;;
        -?*)
            printf "$0 WARN: Unknown option (ignored): %s\n" "$1" >&2
            ;;
        *)               # Default case: No more options, so break out of the loop.
            break
    esac
    shift
done

if [ -z "$FCL" ]; then
  echo "$0 ERROR: fcl is mandatory"
  exit 2
fi

#We need to extract what the default run number is.  Let's get this from running lar and dumping the config
lar --debug-config lar_config_dump.txt -c $FCL
DEFAULTRUN=`grep -r "firstRun" lar_config_dump.txt`
#THis line is of the form firstRun: RUN
#We need to extract RUN
#Delimit on the colon
IFS=\: read -a DEFAULTRUNARRAY <<<"$DEFAULTRUN"
#Extract the run number
DEFAULTRUN=${DEFAULTRUNARRAY[1]}
#Get the subrun candidate number.  We will need to do some modulo arithmetic to work out the actual run and subrun numbers
let "SUBRUNCANDIDATE= $PROCESS +1"
#Calculate how much to increment the run by
RUNINCREMENT=`python -c "print $SUBRUNCANDIDATE//$NSUBRUNSPERRUN"`
#Calculate the run number
let "RUNNUMBER= $DEFAULTRUN + $RUNINCREMENT"
#Now the subrun
SUBRUNNUMBER=`python -c "print $SUBRUNCANDIDATE % $NSUBRUNSPERRUN"`
echo "#Metadata injection by $0" >> $FCL
echo "source.firstRun: $RUNNUMBER" >> $FCL
echo "source.firstSubRun: $SUBRUNNUMBER" >> $FCL
#for singlepi0
echo "process_name: SinglesGen" >> $FCL
echo "outputs.out1.fileName : \"prod_electronpiplus_workshop_icarus_%tc_gen.root\" " >> $FCL
echo "physics.producers.generator.PadOutVectors: true" >> $FCL
echo "physics.producers.generator.PDG: [11, 211]      # Electron, Pi+" >> $FCL
echo "physics.producers.generator.PDist: 2                # Histogram momentum dist." >> $FCL
echo "physics.producers.generator.HistogramFile: \"ParticleGunHists/particlegun_bnb_hists.root\"" >> $FCL
echo "physics.producers.generator.PHist: [ \"hPHist_electrons\", \"hPHist_pi\" ]" >> $FCL
echo "physics.producers.generator.P0: @erase" >> $FCL
echo "physics.producers.generator.SigmaP: @erase" >> $FCL
echo "physics.producers.generator.X0: [ -215.95, -215.95]" >> $FCL
echo "physics.producers.generator.SigmaX: [ 0 ]" >> $FCL
echo "physics.producers.generator.Y0: [0, 0]" >> $FCL
echo "physics.producers.generator.SigmaY: [ 0 ]" >> $FCL
echo "physics.producers.generator.Z0: [-15,-15]" >> $FCL
echo "physics.producers.generator.SigmaZ: [ 0 ]" >> $FCL
echo "physics.producers.generator.T0: [0, 0]" >> $FCL
echo "physics.producers.generator.AngleDist: 0" >> $FCL
echo "physics.producers.generator.ThetaXzYzHist: [ \"hThetaXzYzHist_electrons\" ]" >> $FCL
echo "physics.producers.generator.Theta0XZ: [0, 0]" >> $FCL
echo "physics.producers.generator.Theta0YZ: [0, 0]" >> $FCL
echo "physics.producers.generator.SigmaThetaXZ: [180]" >> $FCL
echo "physics.producers.generator.SigmaThetaYZ: [180]" >> $FCL
echo "physics.producers.generator.HistogramFile: \"$CONDOR_DIR_INPUT/particlegun_bnb_hists.root\"" >> $FCL
