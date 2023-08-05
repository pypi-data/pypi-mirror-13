from distutils.core import setup, Extension

setup(
	name = 'featurehash',
	version = '1.0.2',
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
	>>> featurehash.transform_feature("abc")   #return the code and the sign of hashcode;the code is equal to "hashcode mod 8388608(2^23) + 1"
		(2255879, -1.0)
	>>> featurehash.transform_features(["abc","edf","efd","123","efd"]) #pass a sequence to the function,return the sorted unique feature code.
		[124, 2255879, 3759816, 8023169]
	>>> featurehash.transform_features(["abc","edf","efd","123","efd"],8388607) #pass a sequence and upper_bound;upper_bound default 8388608(2^23)
	[124, 2256031, 3760024, 8023393]
	>>> featurehash.transform_features(["abc","edf","efd","123","efd"],8388607,0) #pass a sequence , upper_bound and min value; min value default 1;
	[123, 2256030, 3760023, 8023392]
	>>> featurehash.transform_features(["abc","edf","efd","123","efd"],8388607,1,1) #pass a sequence , upper_bound, min value and seed; seed value default 0;the same application must must the same seed,ensure the consistent value.
	[124, 661165, 3231265, 8317658]

Modified by jianghuachinacom@163.com

zsp windows,linux python lib
"""
)
