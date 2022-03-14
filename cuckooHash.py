import random
import pytest
import BitHash
        
class CuckooHash(object):
    def __init__(self, size = 1):
        # if user initializes size to 0, change to 1
        if not size: size = 1
        
        # initialize two hashArrays
        self.__hashArray1 = [None] * size
        self.__hashArray2 = [None] * size
        
        # initialize a variable that will count the number of keys inserted
        self.__numKeys = 0
    
    # return the current number of keys inserted
    def __len__(self): return self.__numKeys
    
    # cuckoo feature: when given a key/data pair, begin by inserting into the
    # first hashArray. If there is something in that bucket, move that to the
    # second hashArray. If there is something there, move it to first one. 
    # Repeat this process until every key is properly placed. Once the threshold
    # of 50 is reached, return the key/data that still needs to be inserted
    # in a tuple with the hashArrays beng worked with.
    def __bounceInsertion(self, k, d, arrayOne = None, arrayTwo = None):
        
        # if no hashArrays are given as parameters, modify self.__hashArray
        # directly (this will happen when called directly by the insert method)
        if arrayOne == None and arrayTwo == None:
            arrayOne, arrayTwo = self.__hashArray1, self.__hashArray2
                    
        # create a boolean that will keep track of whether the current key
        # should be inserted into the first hashArray or the second hashArray
        firstArray = True
        
        # create boolean that will keep track of whether the insert is done
        done = False
        
        # create a threshold that will detect an infinite loop (50 inserts)
        threshold = 0
        
        # continue bouncing between hashArryays until every key/data finds a
        # nest or the threshold is reached
        while not done and threshold < 50:
            
            # use __find to create variables for the two possible nests for
            # the key and whether it was found in either nest
            bucket1, l, bucket2, m = self.__find(k)            
        
            # if trying to insert into the first hashArray and its proper nest
            # is empty, insert the key/data, set done to True to exit while loop
            if firstArray and not arrayOne[bucket1]:
                arrayOne[bucket1] = k, d
                done = True
            
            # if trying to insert into the first hashArray and its proper nest
            # is not empty
            elif firstArray and arrayOne[bucket1]:
                # place it anyway, set the current k, d to be the one that
                # was in that nest                
                newInsert = arrayOne[bucket1]
                arrayOne[bucket1] = k, d
                k, d = newInsert
                
                # set firstArray to False so the next insert occurs in the
                # second hashArray                
                firstArray = False
                
                # increment threshold to keep track of how many times it had
                # to bump a key/data from its nest                
                threshold += 1
                
            # if inserting into second hashArray, repeat the same process 
            elif not firstArray and not arrayTwo[bucket2]:
                arrayTwo[bucket2] = k, d    
                done = True
                
            elif not firstArray and arrayTwo[bucket2]:
                newInsert = arrayTwo[bucket2]
                arrayTwo[bucket2] = k, d
                k, d = newInsert
                                
                firstArray = True  
                threshold += 1
        
        # if a cycle was detected, return the key/data needed to be inserted
        # along with the modified arrays
        if not done: return k, d, arrayOne, arrayTwo
        
        # otherwise, this method was successful so return None instead of k, d
        else: return None, None, arrayOne, arrayTwo
            
    # method will be used for one of two things: 1: either reassigning
    # all of the key/data pairs in the two hashArrays to their proper place 
    # after invoking ResetBitHash() from the BitHash module OR 2) growing the 
    # hash and reassigning all of the key/data pairs to their proper place in 
    # the grown hashArrays
    # This method will return True if all key/data pairs hashed properly
    # and False if there was a cycle
    def __resetOrGrowHash(self, size):
        # remember how many indices need to be checked when rehashing each k, d 
        loop = len(self.__hashArray1)
        
        # if the hash is being grown, double the length of self.__hashArray
        # because the __find() method uses the length of the hashArray to
        # find the proper nest so it needs to be the size of the grown hash
        self.__hashArray1 += ([None] * (size - 1) * len(self.__hashArray1))
        self.__hashArray2 += ([None] * (size - 1) * len(self.__hashArray2))
        
        # create two temporary arrays of the proper size
        newOne = [None] * len(self.__hashArray1)
        newTwo = [None] * len(self.__hashArray2)        
        
        # for each element in the arrays
        for i in range(loop):
        
            # set variables to equal each key/data pair
            cur1 = self.__hashArray1[i]
            cur2 = self.__hashArray2[i]
            
            # if there is a key in that index in the first hashArray
            if cur1:
                # insert it into the temporary array
                key1, data1, newOne, newTwo = \
                    self.__bounceInsertion(cur1[0], cur1[1], newOne, newTwo)
                
                # if a key is returned, __bounceInsertion() failed
                if key1: return False
                        
            # if there is a key in that index in the second hashArray
            if cur2:
                # insert it into the temporary array
                key2, data2, newOne, newTwo = \
                    self.__bounceInsertion(cur2[0], cur2[1], newOne, newTwo)
                
                # if a key is returned, __bounceInsertion() failed
                if key2: return False
        
        # upon success, reassign self's hashArrays to equal the temporary arrays
        self.__hashArray1, self.__hashArray2 = newOne, newTwo
        
        return True
    
    # reset every key in the hash after invoking ResetBiHash()
    def __resetHash(self):
        return self.__resetOrGrowHash(1)
    
    # grow the hash when there are too many keys or there is an insertion cycle.
    # after growing, reassign every key to its proper nest
    def __growHash(self):
        return self.__resetOrGrowHash(2)
    
    # insert a key/data pair using the BitHash module
    def insert(self, k, d):
    
        # use __find to create variables for the two possible nests for
        # the key and whether it was found in either nest
        bucket1, l, bucket2, m = self.__find(k)
        
        # if the key was found in one of its nests, override that data with the
        # new data, return True upon succes
        if l:
            self.__hashArray1[bucket1] = k, d
            return True
        
        if m:
            self.__hashArray2[bucket2] = k, d
            return True
        
        # insert the key/data using __bounceInsertion, reassign proper variables
        k, d, self.__hashArray1, self.__hashArray2 = self.__bounceInsertion(k, d)
        
        # create boolean to remember whether resetting/growing the hash worked
        done = False
        
        # if there is still a key to be inserted, that means insert() has not
        # yet succeeded. alternate between resetting BitHash and growing
        # the hashArray until insert succeeds
        while k:
            
            # while resetting and growing the hash have not worked
            while not done:
                # reset the BitHash module
                BitHash.ResetBitHash()
                # once it worked, exit the loop
                if self.__resetHash() or self.__growHash(): done = True
                                            
            # because the BitHash module has been reset, use __find() to 
            # locate where the key/data should be placed
            bucket1, l, bucket2, m = self.__find(k)
            
            # if the first nest is empty, place the key/data there
            if not self.__hashArray1[bucket1]:
                self.__hashArray1[bucket1] = k, d
                # no key to insert so set k to False to exit the while loop
                k = False
            
            # if the second nest is empty, place the key/data there
            elif not self.__hashArray2[bucket2]: 
                self.__hashArray2[bucket2] = k, d
                # no key to insert so set k to False to exit the while loop  
                k = False         
        
        # if the table is getting full, reset the BitHash module then grow
        if self.__numKeys >= .5 * len(self.__hashArray1):
            
            BitHash.ResetBitHash()
            
            # keep resetting the BitHash module until __growHash() works
            while not self.__growHash(): BitHash.ResetBitHash()
            
        # increment self.__numKeys
        self.__numKeys += 1
        
        # return True upon success
        return True
    
    # return a tuple containing the key's first nest, whether the key was
    # found in its first nest, the key's second nest, and whether the key
    # was found in its second nest
    def __find(self, k):
        
        # hash the key, use this result as the seed for the next hash
        seed = BitHash.BitHash(k)
        
        # set bucket1 equal to the index in the first hashArray where the key
        # may be found
        bucket1 = seed % len(self.__hashArray1)
        
        # set bucket2 equal to the index in the second hashArray where the key
        # may be found (use the seed variable as the seed when hashing)
        bucket2 = BitHash.BitHash(k, seed) % len(self.__hashArray2)
        
        # set l equal to the first nest
        l = self.__hashArray1[bucket1]
        
        # if there is a keyData in that nest, and that key is equal to the
        # key being searched for, return the nests and the k, d
        if l and l[0] == k: return bucket1, l, bucket2, None  
        
        # set m equal to the second nest
        m = self.__hashArray2[bucket2]
        
        # if there is a keyData in that nest, and that key is equal to the
        # key being searched for, return the nests and the k, d
        if m and m[0] == k: return bucket1, None, bucket2, m    
        
        # if the key was not found, return the two nests with no k, d
        return bucket1, None, bucket2, None      
    
    # return the data associated with the key k
    def find(self, k):
        # use __find to locate where the key would be placed if it were found
        # and whether the key was found
        bucket1, l, bucket2, m = self.__find(k)
        
        # if the key was found in its first nest, return its data
        if l: return l[1]
        
        # if the key was found in its second nest, return its data
        if m: return m[1]
        
        # if the key was not found, return None
        return None
    
    # remove the element from the hashArray whose key is k   
    def delete(self, k): 
        # use __find to figure out whether the key was found        
        bucket1, l, bucket2, m = self.__find(k)
        
        # if the key was found in its first nest
        if l:
            # set that index of the hashArray to None
            self.__hashArray1[bucket1] = None
            # decrement __numKeys
            self.__numKeys -= 1
            # return the keyData that was removed
            return l
        
        # if the key was found in its second nest
        if m:
            # set that index of the hashArray to None
            self.__hashArray2[bucket2] = None
            # decrement __numKeys
            self.__numKeys -= 1
            # return the keyData that was removed
            return m
        
        # if the key was not found in either nest, return False
        return False
    
    # print all of the key/data pairs starting from index 0 of hashArray1,
    # then index 0 of hashArray2, etc.
    def display(self):
        
        # for each index of the hashArrays
        for i in range(len(self.__hashArray1)):
            
            # set cur1 equal to the key/data pair in hashArray1
            cur1 = self.__hashArray1[i]
            # if there is a key in that index
            if cur1:
                # print the key/data pair
                print("key:", cur1[0], "data:", cur1[1])
            
            # set cur2 equal to the key/data pair in hashArray2               
            cur2 = self.__hashArray2[i]
            # if there is a key in that index
            if cur2:
                # print the key/data pair
                print("key:", cur2[0], "data:", cur2[1])
    
    # use in pytests to confirm that the CuckooHash is, in fact, a CuckooHash
    def isCuckoo(self):
                
        # loop through hashArrays
        for i in range(len(self.__hashArray1)):
            
            # set variables to equal index i in each hashArray
            cur1 = self.__hashArray1[i]
            cur2 = self.__hashArray2[i]
            
            # if there is a key in the first hashArray at that index
            if cur1:
                # hash it
                bucket1 = BitHash.BitHash(cur1[0]) % len(self.__hashArray1)
                
                # if it does not fall into its proper bucket, return False
                if i != bucket1: return False
                            
            # if there is a key in the second hashArray at that index    
            if cur2:
                # hash it twice to find its proper place in the second hashArray
                seed = BitHash.BitHash(cur2[0])
                bucket2 = BitHash.BitHash(cur2[0], seed) % len(self.__hashArray2)
                
                # if it does not fall into its proper bucket, return False
                if i != bucket2: return False
                                            
        return True
    
    # return the key/data pairs in each hashArray
    def pairs(self):
        # loop through hashArrays
        for i in range(len(self.__hashArray1)):
            
            # set variables to equal index i in each hashArray
            cur1 = self.__hashArray1[i]
            cur2 = self.__hashArray2[i]
            
            # if there is a key in the current index, yield that key/data
            if cur1:
                yield cur1[0], cur1[1]
            if cur2:
                yield cur2[0], cur2[1]
            
            
# fake cuckoo class to use in pytests
class FakeCuckoo(object):
    # create dictionary
    def __init__(self): self.__c = {}

    # to take len, take len of dictionary
    def __len__(self): return len(self.__c)  
    
    # to insert, add key/data to dictionary, return True upon success
    def insert(self, k, d): 
        self.__c[k] = d
        return True
    
    # find a key's corresponding data using built-in dictionary method
    def find(self, k): 
        if k in self.__c: return self.__c[k]
    
    # to remove, remember the key/data, delete it, return it
    def delete(self, k):
        if k in self.__c:
            ans = self.__c[k]
            del self.__c[k]
            return ans
    
    # return the keys of the dictionary
    def keys(self): return self.__c.keys()
    
    # return the key/data pairs of the dictionary    
    def pairs(self): return self.__c.items()

# utility function that asserts that the FakeHash and CuckooHash have the
# same key/data pairs
def sameHashes(f, c):
    # test that they have the same len
    assert len(f) == len(c)
    
    fPairs = sorted(f.pairs())
    cPairs = sorted(c.pairs())
    
    # test that they have the same key/data pairs
    assert fPairs == cPairs
    
    # test that each key has the same data    
    for k in f.keys():
        assert f.find(k) == c.find(k)
        
# test that a CuckooHash can accept inserts when invoked without an initial size
def test_emptyCuckoo():
    c = CuckooHash()
    f = FakeCuckoo()
    
    # insert many key/data pairs
    for i in range(20):
        f.insert(i, i)        
        c.insert(i, i)
                
    assert c.isCuckoo()
    sameHashes(f, c)
    
    # test that cuckooHash has the proper len 
    assert len(c) == len(f) == 20

# test that a CuckooHash initialized to size zero can accept inserts        
def test_zeroCuckoo():
    c = CuckooHash(0)
    f = FakeCuckoo()
    
    # insert many key/data pairs    
    for i in range(20):
        f.insert(i, i)        
        c.insert(i, i)
                
    assert c.isCuckoo()
    sameHashes(f, c)
    
    # test that cuckooHash has the proper len     
    assert len(c) == len(f) == 20

# test that the __len__ method returns the proper number of keys
def test_lenCuckoo():
    
    c = CuckooHash(5)
    
    r = random.randint(1, 10000)
    
    # insert many keys
    for i in range(r):
        c.insert(i, i)
        
        # test that len is correct after each insert
        assert len(c) == i + 1
    
    assert c.isCuckoo()
    # after inserting r keys, len should be equal to r        
    assert len(c) == r
   
    # remove all keys
    for i in range(r):
        c.delete(i)
        
        # test that len is correct after each remove
        assert len(c) == r - i - 1
    
    assert c.isCuckoo()
    # after removing all keys, len should be zero    
    assert len(c) == 0

# test that CuckooHash and FakeHash have same inserts with an intiial size
# smaller than the amount of keys being inserted
def test_insertSimpleSmall():
    c = CuckooHash(5)
    f = FakeCuckoo()
    
    # insert key/data
    for i in range(100):
        f.insert(i, i)        
        c.insert(i ,i)
        
    assert c.isCuckoo()
    sameHashes(f, c)

# test that CuckooHash and FakeHash have the same inserts with an intiial size
# larger than the amount of keys being inserted
def test_insertSimpleBig():
    c = CuckooHash(200)
    f = FakeCuckoo()
    
    # insert key/data
    for i in range(100):
        f.insert(i, i)        
        c.insert(i ,i)
        
    assert c.isCuckoo()
    sameHashes(f, c)

# test that when a key is already hashed, insert overrides the old data
def test_insertDouble():
    c = CuckooHash(5)
    f = FakeCuckoo()
    
    # insert a key five times with new data each time
    for i in range(5):
        c.insert(3, i)
        f.insert(3, i)
    
    assert c.isCuckoo()    
    # test that only one key was inserted
    assert len(c) == len(f) == 1    
    sameHashes(f, c)
    
    # assert that 3's data is the latest data being inserted
    assert c.find(3) == f.find(3) == 4

# test that a CuckooHash that is initialized to 5 will grow to fit many keys
def test_insertOverload():
    c = CuckooHash(5)
    f = FakeCuckoo()
    
    for i in range(100000):
        c.insert(i, i)
        f.insert(i, i)
        
    sameHashes(f, c)
    assert c.isCuckoo()

# test that CuckooHash and FakeCuckoo have the same inserts when many keys are
# inserted and removed, test that CuckooHash has the right len and that it is
# still a CuckooHash
def test_torture():
    c = CuckooHash(100)
    f = FakeCuckoo()
    
    r = random.randint(1, 100000)
    
    # insert many keys
    for i in range(r):
        f.insert(i, i)
        c.insert(i, i)
        
        # test that the len is correct after each insert
        assert len(c) == len(f) == i + 1
        
    assert c.isCuckoo()
    sameHashes(f, c)
    
    # remove all keys    
    for i in range(r):
        f.delete(i)
        c.delete(i)
        
        # test that the len is correct after each deletion
        assert len(c) == len(f) == r - i - 1
        
    assert c.isCuckoo()
    sameHashes(f, c)
    # test that the len is zero after all keys are removed
    assert len(c) == len(f) == 0

# test the find() method
def test_findCuckoo():
    c = CuckooHash(10)
    f = FakeCuckoo()
    
    r = random.randint(1, 10000)
    
    # insert many keys
    for i in range(r):
        f.insert(i, i + 1)
        c.insert(i, i + 1)
        
    assert c.isCuckoo()
    sameHashes(f, c)
    
    # test that find() returns the same data as what's in FakeCuckoo, and as
    # what was inserted
    for i in range(r):
        assert c.find(i) == f.find(i) == i + 1

# test that remove() will fail if the key is not found
def test_deleteCuckoo():
    c = CuckooHash(5)
    f = FakeCuckoo()
    
    # insert keys into CuckooHash
    for i in range(100):
        c.insert(i, i)
        f.insert(i, i)
    
    assert c.isCuckoo()       
    sameHashes(f, c)
    
    # remove all keys from CuckooHash    
    for i in range(100):
        c.delete(i)
        f.delete(i)
            
    assert c.isCuckoo()
    sameHashes(f, c)
    
    # the len should be zero after all keys are removed
    assert len(c) == 0
    
    # test that it will fail to remove a key that is not found in CuckooHash
    assert not c.delete(5)
    assert not c.delete(6)
        

pytest.main(["-v", "-s", "cuckooHash.py"])
