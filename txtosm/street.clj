;; experimenting with the core logic for txtosm:

(ns jcgs.street
  (:require [cheshire.core :refer :all]))

(defonce street-name "Štúrova")

(defonce raw-street (parse-stream (clojure.java.io/reader "../sturova.json")))
(defonce raw-elements (raw-street "elements"))

(println (str (count raw-street)) " elements")

(def points (into {} (for [p (filter #(= (% "type") "node") raw-elements)]
                       {(p "id") [(p "lon") (p "lat")]})))
(println (str (count points) " points"))

(def highways (into {}
                    (for [h (filter #(and (= (% "type") "way")
                                          (contains? % "tags")
                                          ;; TODO: I think there's a more idiomatic way to do this
                                          (contains? (% "tags") "highway"))
                                    raw-elements)]
                      {(h "id") h})))
(println (str (count highways) " highways"))

(def main-street (into {} (filter #(and
                                     (contains? (second %) "tags")
                                     (contains? ((second %) "tags") "name")
                                     (= (((second %) "tags") "name") street-name))
                                  highways)))

(println "Parts of main street are " main-street)
