/* 
 * File:   PPL2LigandPO.h
 * Author: zhang
 *
 * Created on March 24, 2014, 11:17 AM
 */

#ifndef PPL2LIGANDPO_H
#define	PPL2LIGANDPO_H

#include <string>

struct POdata{
    std::string sdfFile;
    std::string outputFile;
    std::string xmlOut;
    std::string cmpName;
    int firstLigID;
    bool restart;
    int version;
};

bool PPL2LigandPO(int argc, char** argv, POdata& podata);

#endif	/* PPL2LIGANDPO_H */

