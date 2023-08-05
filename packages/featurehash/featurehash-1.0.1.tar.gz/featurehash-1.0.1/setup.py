from distutils.core import setup, Extension

setup(
	name = 'featurehash',
	version = '1.0.1',
	author = 'Hua Jiang,Bingqing Qu',
	ext_modules = [
	    Extension('featurehash', ['featurehash.cpp'],),
	    ],
	description="MurmurHash3 https://code.google.com/p/smhasher/",
	long_description="""
murmurhash is a fast hash function ::
    >>> import featurehash
	>>> featurehash.hash("abc")  #return the hashcode of the string "abc"
		-1277324294
	>>> featurehash.transform_feature("abc")   #return the code and the sign of hashcode;the code is equal to "hashcode mod 8388608"
		(2255878, -1.0)
	>>> featurehash.transform_features(["abc","edf","efd","123","efd"]) #pass a sequence to the function,return the sorted unique feature code.
		[123, 2255878, 3759815, 8023168]
	>>> featurehash.transform_features(["abc","edf","efd","123","efd"],8388607) #pass a sequence and upper_bound;upper_bound default 8388608(2^23)
	[123, 2256030, 3760023, 8023392]
	>>> featurehash.transform_features(["abc","edf","efd","123","efd"],8388607,1) #pass a sequence , upper_bound and seed; seed default 0;the same application use the same seed value.
	[123, 661164, 3231264, 8317657]

Modified by jianghua@emar.com

zsp windows,linux python lib
"""
)
