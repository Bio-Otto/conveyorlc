/* 
 * File:   XMLDocument.h
 * Author: zhang
 *
 * Created on November 30, 2011, 9:54 PM
 */

#ifndef XMLDOCUMENT_H
#define	XMLDOCUMENT_H

#include <stdio.h>

#include "XMLNode.h"
#include "XMLUtils.hpp"

/** Always the top level node. A document binds together all the
        XML pieces. It can be saved, loaded, and printed to the screen.
        The 'value' of a document node is the xml file name.
 */

namespace LBIND{

class XMLDocument : public XMLNode {
public:
    /// Create an empty document, that has no name.
    XMLDocument();
    /// Create a document with a name. The name of the document is also the filename of the xml.
    XMLDocument(const char * documentName);

    /// Constructor.
    XMLDocument(const std::string& documentName);

    XMLDocument(const XMLDocument& copy);
    XMLDocument& operator=(const XMLDocument& copy);

    virtual ~XMLDocument() {
    }

    /** Load a file using the current document value.
            Returns true if successful. Will delete any existing
            document data before loading.
     */
    bool LoadFile(XMLEncoding encoding = XML_DEFAULT_ENCODING);
    /// Save a file using the current document value. Returns true if successful.
    bool SaveFile() const;
    /// Load a file using the given filename. Returns true if successful.
    bool LoadFile(const char * filename, XMLEncoding encoding = XML_DEFAULT_ENCODING);
    /// Save a file using the given filename. Returns true if successful.
    bool SaveFile(const char * filename) const;
    /** Load a file using the given FILE*. Returns true if successful. Note that this method
            doesn't stream - the entire object pointed at by the FILE*
            will be interpreted as an XML file. TinyXML doesn't stream in XML from the current
            file location. Streaming may be added in the future.
     */
    bool LoadFile(FILE*, XMLEncoding encoding = XML_DEFAULT_ENCODING);
    /// Save a file using the given FILE*. Returns true if successful.
    bool SaveFile(FILE*) const;


    bool LoadFile(const std::string& filename, XMLEncoding encoding = XML_DEFAULT_ENCODING) ///< STL std::string version.
    {
        return LoadFile(filename.c_str(), encoding);
    }

    bool SaveFile(const std::string& filename) const ///< STL std::string version.
    {
        return SaveFile(filename.c_str());
    }


    /** Parse the given null terminated block of xml data. Passing in an encoding to this
            method (either XML_ENCODING_LEGACY or XML_ENCODING_UTF8 will force TinyXml
            to use that encoding, regardless of what TinyXml might otherwise try to detect.
     */
    virtual const char* Parse(const char* p, XMLParsingData* data = 0, XMLEncoding encoding = XML_DEFAULT_ENCODING);

    /** Get the root element -- the only top level element -- of the document.
            In well formed XML, there should only be one. TinyXml is tolerant of
            multiple elements at the document level.
     */
    const XMLElement* RootElement() const {
        return FirstChildElement();
    }

    XMLElement* RootElement() {
        return FirstChildElement();
    }

    /** If an error occurs, Error will be set to true. Also,
            - The ErrorId() will contain the integer identifier of the error (not generally useful)
            - The ErrorDesc() method will return the name of the error. (very useful)
            - The ErrorRow() and ErrorCol() will return the location of the error (if known)
     */
    bool Error() const {
        return error;
    }

    /// Contains a textual (english) description of the error if one occurs.

    const char * ErrorDesc() const {
        return errorDesc.c_str();
    }

    /** Generally, you probably want the error string ( ErrorDesc() ). But if you
            prefer the ErrorId, this function will fetch it.
     */
    int ErrorId() const {
        return errorId;
    }

    /** Returns the location (if known) of the error. The first column is column 1, 
            and the first row is row 1. A value of 0 means the row and column wasn't applicable
            (memory errors, for example, have no row/column) or the parser lost the error. (An
            error in the error reporting, in that case.)

            @sa SetTabSize, Row, Column
     */
    int ErrorRow() const {
        return errorLocation.row + 1;
    }

    int ErrorCol() const {
        return errorLocation.col + 1;
    } ///< The column where the error occured. See ErrorRow()

    /** SetTabSize() allows the error reporting functions (ErrorRow() and ErrorCol())
            to report the correct values for row and column. It does not change the output
            or input in any way.
		
            By calling this method, with a tab size
            greater than 0, the row and column of each node and attribute is stored
            when the file is loaded. Very useful for tracking the DOM back in to
            the source file.

            The tab size is required for calculating the location of nodes. If not
            set, the default of 4 is used. The tabsize is set per document. Setting
            the tabsize to 0 disables row/column tracking.

            Note that row and column tracking is not supported when using operator>>.

            The tab size needs to be enabled before the parse or load. Correct usage:
            @verbatim
            XMLDocument doc;
            doc.SetTabSize( 8 );
            doc.Load( "myfile.xml" );
            @endverbatim

            @sa Row, Column
     */
    void SetTabSize(int _tabsize) {
        tabsize = _tabsize;
    }

    int TabSize() const {
        return tabsize;
    }

    /** If you have handled the error, it can be reset with this call. The error
            state is automatically cleared if you Parse a new XML block.
     */
    void ClearError() {
        error = false;
        errorId = 0;
        errorDesc = "";
        errorLocation.row = errorLocation.col = 0;
        //errorLocation.last = 0; 
    }

    /** Write the document to standard out using formatted printing ("pretty print"). */
    
    void Print() const {
        Print(stdout, 0);
    }

    /* Write the document to a string using formatted printing ("pretty print"). This
            will allocate a character array (new char[]) and return it as a pointer. The
            calling code pust call delete[] on the return char* to avoid a memory leak.
     */
    //char* PrintToMemory() const; 

    /// Print this Document to a FILE stream.
    virtual void Print(FILE* cfile, int depth = 0) const;
    // [internal use]
    void SetError(int err, const char* errorLocation, XMLParsingData* prevData, XMLEncoding encoding);

    virtual const XMLDocument* ToDocument() const {
        return this;
    } ///< Cast to a more defined type. Will return null not of the requested type.

    virtual XMLDocument* ToDocument() {
        return this;
    } ///< Cast to a more defined type. Will return null not of the requested type.

    /** Walk the XML tree visiting this node and all of its children. 
     */
    virtual bool Accept(XMLVisitor* content) const;

protected:
    // [internal use]
    virtual XMLNode* Clone() const;

    virtual void StreamIn(std::istream * in, std::string * tag);


private:
    void CopyTo(XMLDocument* target) const;

    bool error;
    int errorId;
    std::string errorDesc;
    int tabsize;
    XMLCursor errorLocation;
    bool useMicrosoftBOM; // the UTF-8 BOM were found when read. Note this, and try to write.
};

} //namespace LBIND

#endif	/* XMLDOCUMENT_H */

