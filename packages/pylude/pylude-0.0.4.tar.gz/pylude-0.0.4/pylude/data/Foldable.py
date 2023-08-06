

#https://hackage.haskell.org/package/base-4.8.1.0/docs/Data-Foldable.html#t:Foldable

"""
Class of data structures that can be folded to a summary value.


Data structures that can be folded.

For example, given a data type

data Tree a = Empty | Leaf a | Node (Tree a) a (Tree a)

a suitable instance would be

instance Foldable Tree where
   foldMap f Empty = mempty
   foldMap f (Leaf x) = f x
   foldMap f (Node l k r) = foldMap f l `mappend` f k `mappend` foldMap f r

This is suitable even for abstract types, as the monoid is assumed to satisfy the monoid laws. Alternatively, one could define foldr:

instance Foldable Tree where
   foldr f z Empty = z
   foldr f z (Leaf x) = f x z
   foldr f z (Node l k r) = foldr f (f k (foldr f z r)) l

Foldable instances are expected to satisfy the following laws:

foldr f z t = appEndo (foldMap (Endo . f) t ) z

foldl f z t = appEndo (getDual (foldMap (Dual . Endo . flip f) t)) z

fold = foldMap id

sum, product, maximum, and minimum should all be essentially equivalent to foldMap forms, such as

sum = getSum . foldMap Sum

but may be less defined.

If the type is also a Functor instance, it should satisfy

foldMap f = fold . fmap f

which implies that

foldMap f . fmap g = foldMap (f . g)

"""

class Foldable:
    pass



#fold


#foldMap


#foldr


#foldl


#toList


#elem

