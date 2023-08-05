// Feature Hashing
//
// MurMurHash3 originally created by Austin Appleby at:
// https://code.google.com/p/smhasher/
//
// This is the original claim
//-----------------------------------------------------------------------------
// MurmurHash3 was written by Austin Appleby, and is placed in the public
// domain. The author hereby disclaims copyright to this source code.

// Note - The x86 and x64 versions do _not_ produce the same results, as the
// algorithms are optimized for their respective platforms. You can still
// compile and run any of them on any platform, but your performance with the
// non-native version will be less than optimal.
//-----------------------------------------------------------------------------
//
// @adopted by : Bingqing Qu <qubingqing@emar.com>
//
// @Version : 0.0.1 (alpha)


//-----------------------------------------------------------------------------
// Platform-specific functions and macros

// Microsoft Visual Studio

#if defined(_MSC_VER) && (_MSC_VER < 1600)

typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef unsigned __int64 uint64_t;

// Other compilers

#else   // defined(_MSC_VER)

#include <stdint.h>

#endif // !defined(_MSC_VER)

#if defined(_MSC_VER)

#define ROTL32(x,y)	 _rotl(x,y)
#define ROTL64(x,y)	 _rotl64(x,y)

#define BIG_CONSTANT(x) (x)

// Other compilers

#else   // defined(_MSC_VER)

inline uint32_t rotl32 ( uint32_t x, int8_t r )
{
	return (x << r) | (x >> (32 - r));
}

#define ROTL32(x,y)	 rotl32(x,y)

#define BIG_CONSTANT(x) (x##LLU)

#endif // !defined(_MSC_VER)

#include <Python.h>
#include <string>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <vector>
#include <map>

template<class T>
T _hashing ( const void * key, const int len, const uint32_t seed);

//-----------------------------------------------------------------------------
// Block read - if your platform needs to do endian-swapping or can only
// handle aligned reads, do the conversion here

inline uint32_t getblock32 ( const uint32_t * p, int i )
{
	return p[i];
}

//-----------------------------------------------------------------------------
// Finalization mix - force all bits of a hash block to avalanche

inline uint32_t fmix32 ( uint32_t h )
{
	h ^= h >> 16;
	h *= 0x85ebca6b;
	h ^= h >> 13;
	h *= 0xc2b2ae35;
	h ^= h >> 16;

	return h;
}

//-----------------------------------------------------------------------------

template<class T>
T _hashing ( const void * key, int len, uint32_t seed)
{
	const uint8_t * data = (const uint8_t*)key;
	const int nblocks = len / 4;

	uint32_t h1 = seed;

	const uint32_t c1 = 0xcc9e2d51;
	const uint32_t c2 = 0x1b873593;

	//----------
	// body

	const uint32_t * blocks = (const uint32_t *)(data + nblocks*4);

	for(int i = -nblocks; i; i++)
	{
		uint32_t k1 = getblock32(blocks,i);

		k1 *= c1;
		k1 = ROTL32(k1,15);
		k1 *= c2;

		h1 ^= k1;
		h1 = ROTL32(h1,13);
		h1 = h1*5+0xe6546b64;
	}

	//----------
	// tail

	const uint8_t * tail = (const uint8_t*)(data + nblocks*4);

	uint32_t k1 = 0;

	switch(len & 3)
	{
		case 3: k1 ^= tail[2] << 16;
		case 2: k1 ^= tail[1] << 8;
		case 1: k1 ^= tail[0];
			k1 *= c1; k1 = ROTL32(k1,15); k1 *= c2; h1 ^= k1;
	};

	//----------
	// finalization

	h1 ^= len;

	h1 = fmix32(h1);

	return (T)h1;
}

#ifndef ABS
template<class T> inline T ABS(T x){ return (x<0?-x:x);}
#endif


/**
 * Transform String feature to hashed value. This will ignore
 * pure number as it regard digits (number) as already hashed and
 * a modulo operator will be followed.
 *
 * @param feature input string
 * @return hashed value of input string
 */
uint32_t feature_hashing(const char* c_feature,unsigned int len,double& sign,uint32_t upper_bound_=8388608,uint32_t seed_=0)
{
	// use hacked strtol to check if the string is a pure number
	// one excpetion is if the first digit of input string is whitespace
	// as we only check if the string is a number of not
	char* p;
	long converted = strtol(c_feature, &p, 10);
	int32_t hashed_value;
	if (*p) {
		hashed_value = _hashing<int32_t>(c_feature,len,seed_);
		sign = hashed_value <0 ? -1.0 : 1.0;
		return ABS(hashed_value) % upper_bound_;
	}
	else {
		sign = converted <0 ? -1.0 : 1.0;
		return ABS(converted) % upper_bound_;
	}
}

std::vector<uint32_t> features_hashing(const std::vector<std::string> features)
{
	std::map<uint32_t,double> values;
	std::vector<uint32_t> hashed;
	hashed.reserve(features.size());
	uint32_t index = 0;
	double sign = 0;
	for(size_t i = 0; i < features.size();++i)
	{
		index = feature_hashing(features[i].c_str(),features[i].length(),sign);
		values[index] += sign;
	}
	std::multimap<uint32_t,double>::iterator iter = values.begin();
	for (;iter!=values.end();++iter)
	{
		if(iter->second!=0)
		{
			hashed.push_back(iter->first);
		}
	}
	return hashed;
}



static PyObject * transform_features_test(PyObject *self,PyObject *args) {
	std::vector<std::string> features;
	PyObject* pList;
	PyObject *arg;
	double sign = 0;
	uint32_t upper_bound=8388608;
	uint32_t seed=0;
	int size=0;
	uint32_t rs2=0;
	char *p;
	unsigned int len;
	if(!PyArg_ParseTuple(args,"O",&arg)) {
		return NULL;
	}
	if(PySequence_Check(arg)){
		size=PySequence_Size(arg);
		features.reserve(size);
		for(int i=0;i<size;i++){
			PyObject *item;
	        item = PySequence_GetItem(arg, i);
			p=PyString_AS_STRING(item);
			features.push_back(p);
		}
		std::vector<uint32_t> hashed = features_hashing(features);
		pList= PyList_New(hashed.size());
		for(int i=0;i<hashed.size();i++){
			PyList_SetItem(pList,i, Py_BuildValue("i",hashed[i]));
		}
	}
	return pList;
}

static PyObject * transform_features(PyObject *self,PyObject *args) {
	PyObject* pList;
	PyObject *arg;
	uint32_t upper_bound=8388608;
	uint32_t seed=0;
	if(!PyArg_ParseTuple(args,"O|ii",&arg,&upper_bound,&seed)) {
		return NULL;
	}
	if(PySequence_Check(arg)){
		uint32_t index = 0;
		double sign = 0;
		int size=PySequence_Size(arg);
		std::map<uint32_t,double> values;
		for(int i=0;i<size;i++){
			PyObject *item=PySequence_GetItem(arg, i);
			std::string feature=PyString_AS_STRING(item);
			index = feature_hashing(feature.c_str(),feature.length(),sign,upper_bound,seed);
			values[index] += sign;
		}
		std::multimap<uint32_t,double>::iterator iter = values.begin();
		pList= PyList_New(0);
		//int i=0;
		for (;iter!=values.end();++iter)
		{
			if(iter->second!=0)
			{
				//PyList_SetItem(pList,i, Py_BuildValue("i",iter->first));
				PyList_Append(pList,Py_BuildValue("i",iter->first));
				//i++;
			}
		}
	}
	return pList;
}

static PyObject * transform_feature(PyObject *self,PyObject *args) {
	char * c_feature;
	double sign = 0;
	uint32_t upper_bound=8388608;
	uint32_t seed=0;
	unsigned int len;
	if(!PyArg_ParseTuple(args,"s#|ii",&c_feature,&len,&upper_bound,&seed)) {
		return NULL;
	}
	uint32_t h =  feature_hashing(c_feature,len,sign,upper_bound,seed);
	return Py_BuildValue("id",h,sign);
}


static PyObject * hash(PyObject *self,PyObject *args) {
	char * c_feature;
	uint32_t seed=0;
	int32_t hashed_value;
	unsigned int len;
	if(!PyArg_ParseTuple(args,"s#|i",&c_feature,&len,&seed)) {
		return NULL;
	}
	hashed_value = _hashing<int32_t>(c_feature,len,seed);
	return Py_BuildValue("i",hashed_value);
}

static PyMethodDef methods[] = {
	{"transform_feature",(PyCFunction)transform_feature,METH_VARARGS,""},
	{"transform_features",(PyCFunction)transform_features,METH_VARARGS,""},
	{"hash",(PyCFunction)hash,METH_VARARGS,""},
	{NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initfeaturehash() {
	Py_InitModule3("featurehash", methods, "MurmurHash3 hash algorithm extension module.");
}
