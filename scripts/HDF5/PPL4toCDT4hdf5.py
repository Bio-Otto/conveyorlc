import argparse
import os.path
import datetime
import glob
import conduit
import conduit.relay
import numpy as np
import tarfile
from mpi4py import MPI


"""
Running the serial PPL4conversion on LC

cd <your_running_directory_contains_scratch/lig>

/usr/gapps/bbs/TOSS-3/spack/bin/cdtPython.sh PPL4toCDT4hdf5.py

Or if you provide inputs:

/usr/gapps/bbs/TOSS-3/spack/bin/cdtPython.sh PPL4toCDT4hdf5.py -d <path_to_scratch> -o <path_to_directory_hdf5_files>


Running the parallel version using the script:
--------------
#!/bin/bash
#MSUB -A bbs
#MSUB -l nodes=2
#MSUB -l walltime=16:00:00
#MSUB -l partition=syrah
#MSUB -q pbatch
#MSUB -m be
#MSUB -N x02
#MSUB -e x02.err
#MSUB -o x02.out

ml python
module load gcc/4.9.3
module load mvapich2/2.2

export SPACK_ROOT=/usr/gapps/bbs/TOSS-3/spack
export PATH=$SPACK_ROOT/bin:$PATH
source $SPACK_ROOT/share/spack/setup-env.sh

spack load python
spack load py-mpi4py
spack load py-numpy
spack load hdf5
spack load conduit

srun -N2 -n32 python PPL4toCDT4hdf5.py
---------------


It assume that the scratch/lig has following data structure

scratch/com/<pdbname1>/gbsa/lig_1/pose_1
scratch/com/<pdbname1>/gbsa/lig_1/pose_2
...
scratch/com/<pdbname1>/gbsa/lig_1/pose_L
...
scratch/com/<pdbname1>/gbsa/lig_2/pose_1
...
scratch/com/<pdbname1>/gbsa/lig_N/pose_1
...
scratch/com/<pdbnameM>/gbsa/lig_1/pose_1
...
scratch/com/<pdbnameM>/gbsa/lig_N/pose_L

Each directory must have: 'checkpoint.txt' (Otherwise it will skip the directory)
and may including: 'mmgbsa_results.tar.gz', and other gbsa rescoring files.
"""


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--scrDir', action='store', dest='scrDir', default='scratch',
                        help='path to scratch directory')
    parser.add_argument('-o', '--outDir', action='store', dest='outfile', default='scratch/gbsaHDF5',
                        help='path to gbsaing HDF5 files')

    args = parser.parse_args()

    return args


def filesToHDF(n, cmpdKey, fileList):
    for file in fileList:
        if os.path.isfile(file):
            with open(file, 'r') as f:
                n[cmpdKey + "/file/" + file] = f.read()
        else:
            print("File - "+file+" no found")

def parseCheckpoint(checkfile):
    checkData = {}
    with open(checkfile, "r") as f:
        for line in f:
            strs = line.strip().split(':')
            if len(strs) == 2:
                checkData[strs[0]] = strs[1]

    return checkData

def getID(idStr):
    strs=idStr.split('_')
    if len(strs)==2:
        return strs[1]

    return None

def extract_files(members):
    extractList = ['Com.inpcrd', 'Com.prmtop', 'Com_leap.log',
                   'Com_min.pdb', 'Com_min.rst', 'Com_min_GB.out',
                   'Lig_leap.log', 'Rec_minGB.out', 'rec_leap.log']
    for tarinfo in members:
        if os.path.basename(tarinfo.name) in extractList:
            yield tarinfo


def PPL4toCDT4(args):

    nHeader = conduit.Node()
    nHeader['date'] = "Created by PPL4toCDT4hdf5.py at " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    print("Created by PPL4toCDT4hdf5.py at " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"))

    if not os.path.exists(args.outfile):
        os.makedirs(args.outfile)

    hdf5pathDir = os.path.abspath(args.outfile)
    hdf5path=os.path.join(hdf5pathDir, "gbsa_proc1.hdf5")
    print(hdf5path)

    conduit.relay.io.save(nHeader, hdf5path)

    comDirPath = os.path.abspath(args.scrDir + "/com")
    print(comDirPath)
    os.chdir(comDirPath)
    dirs = os.listdir(".")
    for recid in dirs:
        recPath = os.path.join(comDirPath, recid+"/gbsa")
        if os.path.isdir(recPath):
            os.chdir(recPath)
            print(os.getcwd())

            ligs=os.listdir(".")

            for ligid in ligs:
                ligPath = os.path.join(recPath, ligid)
                if os.path.isdir(ligPath):
                    n = conduit.Node()
                    ligidReal = getID(ligid)
                    os.chdir(ligPath)
                    poses=os.listdir(".")

                    for poseID in poses:
                        posePath=os.path.join(ligPath, poseID)
                        os.chdir(posePath)
                        checkfile=os.path.join(posePath, 'checkpoint.txt')

                        if os.path.isfile(checkfile):
                            poseIDReal=getID(poseID)
                            checkData = parseCheckpoint(checkfile)
                            entryKey = '/gbsa/' + recid+"/"+ligidReal+"/p"+poseIDReal
                            print(checkData)
                            if 'Mesg' in checkData:
                                if checkData['Mesg'] == 'Finished!':
                                    n[entryKey + '/status'] = np.int32(1)
                                else:
                                    n[entryKey + '/status'] = np.int32(0)
                                n[entryKey + '/meta/Mesg'] = checkData['Mesg']

                            if 'GBSA' in checkData:
                                n[entryKey + '/meta/bindGB'] = float(checkData['GBSA'])

                            if 'vina' in checkData:
                                n[entryKey + '/meta/dockScore'] = float(checkData['vina'])

                            mmgbsafile = os.path.join(posePath, 'mmgbsa_results.tar.gz')

                            if os.path.isfile(mmgbsafile):
                                tar = tarfile.open(mmgbsafile)
                                tar.extractall(members=extract_files(tar))
                                tar.close()

                            extractList = ['Com.inpcrd', 'Com.prmtop', 'Com_leap.log',
                                           'Com_min.pdb', 'Com_min.rst', 'Com_min_GB.out',
                                           'Lig_leap.log', 'Rec_minGB.out', 'rec_leap.log']

                            filesToHDF(n, entryKey, extractList)
                            for file in extractList:
                                if os.path.isfile(file):
                                    os.remove(file)

                    conduit.relay.io.save_merged(n, hdf5path)


def PPL4toCDT4_MPI(args):
    comm=MPI.COMM_WORLD
    rank=comm.rank
    size = comm.size
    #print(rank, size)
    if rank==0:
        if not os.path.exists(args.outfile):
            os.makedirs(args.outfile)

    hdf5pathDir = os.path.abspath(args.outfile)

    keyList=[]

    comDirPath = os.path.abspath(args.scrDir + "/com")
    if rank==0:
        print(comDirPath)
    os.chdir(comDirPath)
    dirs = os.listdir(".")

    #for recid in dirs:
    for i in xrange(rank, len(dirs), size):
        recid=dirs[i]
        #print(rank, i, recid)
        recPath = os.path.join(comDirPath, recid+"/gbsa")
        if os.path.isdir(recPath):
            os.chdir(recPath)

            for ligid in glob.glob('lig_*'):
                ligPath = os.path.join(recPath, ligid)
                if os.path.isdir(ligPath):
                    os.chdir(ligPath)
                    for poseID in glob.glob('pose_*'):
                        entryKey=recid+"/"+ligid+"/"+poseID
                        keyList.append(entryKey)


    allKeys=comm.gather(keyList, root=0)

    calcKeyList=[]
    if rank==0:
        for klist in allKeys:
            calcKeyList=calcKeyList+klist

    calcKeyList = comm.bcast(calcKeyList, root=0)

    if rank==0:
        print(rank, calcKeyList)

    calcKeySize=len(calcKeyList)

    if rank<calcKeySize:

        nHeader = conduit.Node()
        nHeader['date'] = "Created by PPL4toCDT4hdf5.py at " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        if rank==0:
            print("Created by PPL4toCDT4hdf5.py at " + datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S"))


        hdf5path=os.path.join(hdf5pathDir, "gbsa_proc"+str(rank)+".hdf5")
        print(rank, hdf5path)

        conduit.relay.io.save_merged(nHeader, hdf5path)

        for i in xrange(rank, calcKeySize, size):
            calcKey=calcKeyList[i]
            strs=calcKey.split("/")
            #print(rank, strs)
            if len(strs)==3:
                recid=strs[0]
                ligid=strs[1]
                poseID=strs[2]
                posePath = os.path.join(comDirPath, recid + "/gbsa/"+ligid+"/"+poseID)
                print(rank, posePath)
                if os.path.isdir(posePath):
                    os.chdir(posePath)

                    checkfile = os.path.join(posePath, 'checkpoint.txt')

                    if os.path.isfile(checkfile):
                        ligidReal=getID(ligid)
                        poseIDReal = getID(poseID)
                        checkData = parseCheckpoint(checkfile)
                        entryKey = '/gbsa/' + recid + "/" + ligidReal + "/p" + poseIDReal
                        print(checkData)
                        n = conduit.Node()
                        if 'Mesg' in checkData:
                            if checkData['Mesg'] == 'Finished!':
                                n[entryKey + '/status'] = np.int32(1)
                            else:
                                n[entryKey + '/status'] = np.int32(0)
                            n[entryKey + '/meta/Mesg'] = checkData['Mesg']

                        if 'GBSA' in checkData:
                            n[entryKey + '/meta/bindGB'] = float(checkData['GBSA'])

                        if 'vina' in checkData:
                            n[entryKey + '/meta/dockScore'] = float(checkData['vina'])

                        mmgbsafile = os.path.join(posePath, 'mmgbsa_results.tar.gz')

                        if os.path.isfile(mmgbsafile):
                            tar = tarfile.open(mmgbsafile)
                            tar.extractall(members=extract_files(tar))
                            tar.close()

                        extractList = ['Com.inpcrd', 'Com.prmtop', 'Com_leap.log',
                                       'Com_min.pdb', 'Com_min.rst', 'Com_min_GB.out',
                                       'Lig_leap.log', 'Rec_minGB.out', 'rec_leap.log']

                        filesToHDF(n, entryKey, extractList)

                        conduit.relay.io.save_merged(n, hdf5path)

                        for file in extractList:
                            if os.path.isfile(file):
                                os.remove(file)

def main():
    comm=MPI.COMM_WORLD
    size=comm.size
    rank=comm.rank

    args = getArgs()

    if rank==0:
        print("Default inputs: ", args.scrDir, args.outfile)

    if size==1:
        PPL4toCDT4(args)
    else:
        PPL4toCDT4_MPI(args)

if __name__ == '__main__':
    main()