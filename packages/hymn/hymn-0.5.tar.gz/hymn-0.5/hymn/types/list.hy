;;; -*- coding: utf-8 -*-
;;; Copyright (c) 2014-2016, Philip Xu <pyx@xrefactor.com>
;;; License: BSD New, see LICENSE for details.
"hymn.types.list - the list monad"

(import
  [itertools [chain]]
  [hymn.types.monadplus [MonadPlus]]
  [hymn.types.monoid [Monoid]]
  [hymn.utils [CachedSequence]])

(defreader * [seq]
  (with-gensyms [List]
    `(do (import [hymn.types.list [List :as ~List]]) (~List ~seq))))

(defclass -Zero [object]
  "descriptor that returns an empty List"
  [[--get-- (fn [self instance cls] (cls []))]])

(defclass List [MonadPlus Monoid]
  "the list monad

  nondeterministic computation"
  [[--init-- (fn [self value] (setv self.value (CachedSequence value)) nil)]
   [--iter-- (fn [self] (iter self.value))]
   [--len-- (fn [self] (len self.value))]
   [fmap (fn [self f]
           "return list obtained by applying :code:`f` to each element of the
           list"
           (List (map f self.value)))]
   [join (fn [self]
           "join of list monad, concatenate list of list"
           (List (chain.from-iterable self)))]
   [append (fn [self other]
             "the append operation of :class:`List`"
             (List (chain self other)))]
   [concat (with-decorator classmethod
             ;; overloaded for better performance
             (fn [cls list-of-list]
               "the concat operation of :class:`List`"
               (List (chain.from-iterable list-of-list))))]
   [plus (fn [self other]
           "concatenate two list"
           (.append self other))]
   [unit (with-decorator classmethod
           (fn [cls &rest values]
             "the unit, create a :class:`List` from :code:`values`"
             (cls values)))]
   [zero (-Zero)]
   [empty zero]])

;;; alias
(def list-m List)
(def unit List.unit)
(def zero List.zero)

(defn fmap [f iterable]
  ":code:`fmap` works like the builtin :code:`map`, but return a :class:`List`
  instead of :code:`list`"
  (list-m (map f iterable)))
