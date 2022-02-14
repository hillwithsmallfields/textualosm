;; experimenting with the core logic for txtosm:

(ns jcgs.street
  (:require [cheshire.core :refer :all]))

(defonce street-name "Štúrova")

(defonce raw-street (parse-stream (clojure.java.io/reader "../sturova.json")))
(defonce raw-elements (raw-street "elements"))

;; (println (str (count raw-street)) " elements")

(def points (into {} (for [p (filter #(= (% "type") "node") raw-elements)]
                       {(p "id") [(p "lon") (p "lat")]})))
;; (println (str (count points) " points"))

(def highways (into {}
                    (for [h (filter #(and (= (% "type") "way")
                                          (get-in % ["tags" "highway"]))
                                    raw-elements)]
                      {(h "id") h})))
;; (println (str (count highways) " highways"))

(def main-street (into {} (filter #(= (get-in (second %) ["tags" "name"])
                                      street-name)
                                  highways)))

(println "main street has " (count main-street) " parts")

(doseq [keyval main-street]
  (println (key keyval) (val keyval)))

(defn first-node-of-section [section]
  (first (section "nodes")))

(defn last-node-of-section [section]
  (last (section "nodes")))

(def main-street-sections-by-first-node
  (into {}
        (for [section (seq main-street)]
          {(first-node-of-section (second section)) section})))

(def main-street-sections-by-last-node
  (into {}
        (for [section (seq main-street)]
          {(last-node-of-section (second section)) section})))

(println "main street has " (count main-street-sections-by-first-node) " sections by first node:")

(doseq [keyval main-street-sections-by-first-node]
  (println (key keyval) (val keyval)))

(def chains-1
  (for [section (seq main-street)]
    (list (second section))))

(doseq [chain chains-1]
  (println "single section: " chain))

(defn extend-chains [chains]
  (for [chain chains]
    (let [starting-node (first-node-of-section (first chain))
          preceding (get main-street-sections-by-last-node starting-node nil)]
      (if preceding
        (cons (second preceding) chain)
        chain))))

(def chains-2
  (extend-chains chains-1))

(doseq [chain chains-2]
  (println "single or double section: " (count chain) chain))

(def chains-3
  (extend-chains chains-2))

(doseq [chain chains-3]
  (println "single, double, or triple section: " (count chain) chain))

;; TODO: recurse as many times as there are sections (minus one)

;; (println "main street has " (count main-street-sections-by-last-node) " sections by last node:")

;; (doseq [keyval main-street-sections-by-last-node]
;;   (println (key keyval) (val keyval)))

;; I think this is wrong:
;; (def nexts
;;   (into {}
;;         (for [section (seq main-street)]
;;           {(first section)
;;            (last-node-of-section (second section))})))

;; (def prevs
;;   (into {}
;;         (for [section (seq main-street)]
;;           {(first section)
;;            (first-node-of-section (second section))})))

;; (println "nexts: " nexts)
;; (println "prevs: " prevs)
