/* 
 * File:   Molecule.h
 * Author: xiaohua
 *
 * Created on May 26, 2009, 7:19 AM
 */

#ifndef _MOLECULE_H
#define	_MOLECULE_H

#include <string>
#include <vector>
#include <map>
#include <boost/shared_ptr.hpp>

#include "BaseStruct.h"

namespace LBIND{
    class Complex;
    class Fragment;
    class Atom;
    class Bond;
    class BondContainer;
    class Ring;
    class RingContainer;

//class Molecule : public boost::enable_shared_from_this<Molecule>{
class Molecule : public BaseStruct {
public:
    Molecule();
    Molecule(Complex* parent);

    Molecule(const Molecule& orig);
    virtual ~Molecule();

    Complex* getParent();

    virtual std::vector<Fragment*> getChildren();
    virtual std::vector<Atom*> getGrdChildren();
    BondContainer* getPBondContainer();    
    RingContainer* getPRingContainer();

    Atom* addAtom();
    Fragment* addFragment();

    int getTotNumAtom();

private:

    double itscharge;

    Complex* pParent;

    std::vector<Fragment*> itsChildren;
    std::vector<Atom*> itsGrdChildren;

    BondContainer* pBondContainer;
    RingContainer* pRingContainer;

};


} //namespace

#endif	/* _MOLECULE_H */
