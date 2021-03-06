/* 
 * File:   file.hpp
 * Author: zhang30
 *
 * Created on August 22, 2012, 5:48 PM
 */

#ifndef FILE_HPP
#define	FILE_HPP

#include <string>
#include <fstream>

#include "Structure/Sstrm.hpp"

namespace LBIND {


inline void getPathName (const std::string& pathStr, std::string& pathName)
{
  size_t found;
  found=pathStr.find_last_of("/\\");
  pathName=pathStr.substr(0,found);

}
    
inline void getPathFileName (const std::string& pathStr, std::string& pathFileName)
{
  size_t found;
  found=pathStr.find_last_of("/\\");
  pathFileName= pathStr.substr(found+1);
} 

inline void getFileBasename(const std::string& pathStr, std::string& pathFileName){
  size_t found;
  found=pathStr.find_last_of("/\\");
  pathFileName= pathStr.substr(found+1);
  found=pathFileName.find_last_of(".");
  pathFileName= pathFileName.substr(0,found);  
}


inline bool fileExist(std::string& pathFile){
    std::ifstream my_file(pathFile.c_str());
    return my_file.good();    
}

inline bool fileEmpty(std::string& pathFile){    
    std::ifstream pFile(pathFile.c_str());
    return pFile.peek() == std::ifstream::traits_type::eof();
}

// !low overhead
inline int getFileSizebyCommand(std::string& pathFile){
    int size=0;
    std::string cmd="ls -l "+pathFile+" |awk '{print $5}' > tmp";
    system(cmd.c_str());
    std::ifstream inFile;
    inFile.open("tmp");
    std::string line;
    std::getline(inFile, line);
    inFile.close();
    size=Sstrm<int, std::string>(line);
    return size;
}

inline int getFileSize( std::string& pathFile )
{

    FILE *pFile = fopen(pathFile.c_str(), "rb" );

    // set the file pointer to end of file
    fseek( pFile, 0, SEEK_END );

    // get the file size
    int size = ftell( pFile );

    // return the file pointer to begin of file if you want to read it
    // rewind( pFile );

    // close stream and release buffer
    fclose( pFile );

    return size;
}

inline bool checkFile(std::string& pathFile){
    if(getFileSize(pathFile) < 10){
        std::string message=pathFile+" is empty.";
//        throw LBindException(message); 
        return false;
    }
    return true;
}
    
}//namespace LBIND 

#endif	/* FILE_HPP */

