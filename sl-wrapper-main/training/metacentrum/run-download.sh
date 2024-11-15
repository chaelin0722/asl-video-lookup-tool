#PBS -N dwnld
#PBS -q runone
#PBS -l walltime=4:00:00

#PBS -l select=1:ncpus=1:cluster=adan:mem=5gb
#PBS -j oe
#PBS -m ae

cd /storage/plzen4-ntis/projects/cv/spoter
# wget https://download.microsoft.com/download/b/8/8/b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip
unzip ASL_Citizen.zip
