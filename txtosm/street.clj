;; experimenting with the core logic for txtosm:

(ns jcgs.street
  (:require [cheshire.core :refer :all]))

(defonce street-name
  ;; "Štúrova"
  "High Street"
  )

(defonce raw-street
  (parse-stream
   (clojure.java.io/reader
    ;; "../sturova.json"
    "../high-street.json"
    )))
(defonce raw-elements (raw-street "elements"))

;; (println (str (count raw-street)) " elements")

(def points (into {} (for [p (filter #(= (% "type") "node") raw-elements)]
                       {(p "id") [(p "lat") (p "lon")]})))
;; (println (str (count points) " points"))

(defn latlon-of-point [point-id]
  (points point-id))

(defn osm-url-of-point [point-id]
  (let [coords (latlon-of-point point-id)]
    (format "https://www.openstreetmap.org/?mlat=%g&mlon=%g#map=18/%g/%g"
            (first coords) (second coords)
            (first coords) (second coords))))

(def radius-of-earth 6371e3)

(defn radians [d]
  (* d (/ Math/PI 180)))

(defn degrees [r]
  (* r (/ 180 Math/PI)))

(defn distance
  ([from to] (let [from-spec (if (int? from)
                               (latlon-of-point from)
                               from)
                   to-spec (if (int? to)
                             (latlon-of-point to)
                             to)]
               (distance (first from-spec) (second from-spec)
                         (first to-spec) (second to-spec))))
  ([lat1 lon1 lat2 lon2]
   (let [φ1 (radians lat1)
         φ2 (radians lat2)
         Δφ (radians (- lat2 lat1))
         Δλ (radians (- lon2 lon1))
         a (+ (* (Math/sin (/ Δφ 2))
                 (Math/sin (/ Δφ 2)))
              (* (Math/cos φ1)
                 (Math/cos φ2)
                 (Math/sin (/ Δλ 2))
                 (Math/sin (/ Δλ 2))))
         c  (* 2  (Math/atan2 (Math/sqrt a)
                              (Math/sqrt (- 1 a))))]
     (* c radius-of-earth))))

(defn bearing
  ([from to] (let [from-spec (if (int? from)
                               (latlon-of-point from)
                               from)
                   to-spec (if (int? to)
                             (latlon-of-point to)
                             to)]
               (bearing (first from) (second from)
                        (first to) (second to))))
  ([lat1 lon1 lat2 lon2]
   (let [φ1 (radians lat1)
         λ1 (radians lon1)
         φ2 (radians lat2)
         λ2 (radians lon2)
         y  (* (Math/sin (- λ2 λ1))
               (Math/cos φ2))
         x  (- (* (Math/cos φ1)
                  (Math/sin φ2))
               (* (Math/sin φ1)
                  (Math/cos φ2)
                  (Math/cos(- λ2 λ1))))
         θ (Math/atan2 y x)]
     (mod (+ (degrees θ)
             360)
          360))))

(defn way-distance [way]
  (let [nodes (if (map? way)
                (way "nodes")
                way)]
    (reduce + (map distance
                   nodes
                   (rest nodes)))))

(defn chain-distance [chain]
  (reduce +
          (map way-distance
               chain)))

(def highways (into {}
                    (for [h (filter #(and (= (% "type") "way")
                                          (get-in % ["tags" "highway"]))
                                    raw-elements)]
                      {(h "id") h})))
;; (println (str (count highways) "highways"))

(def main-street (into {} (filter #(= (get-in (second %) ["tags" "name"])
                                      street-name)
                                  highways)))

(println "main street has" (count main-street) "parts")

(doseq [keyval main-street]
  (println (key keyval) (val keyval)))

(defn first-node-of-section [section]
  (first (section "nodes")))

(defn last-node-of-section [section]
  (last (section "nodes")))

(defn first-node-of-chain [chain]
  (first-node-of-section (first chain)))

(defn last-node-of-chain [chain]
  (last-node-of-section (last chain)))

(def main-street-sections-by-first-node
  (into {}
        (for [section (seq main-street)]
          {(first-node-of-section (second section)) section})))

(def main-street-sections-by-last-node
  (into {}
        (for [section (seq main-street)]
          {(last-node-of-section (second section)) section})))

(println "main street has" (count main-street-sections-by-first-node) "sections by first node:")
(doseq [keyval main-street-sections-by-first-node]
  (println (key keyval) (val keyval)))

(def chains-1
  (for [section (seq main-street)]
    (list (second section))))

(doseq [chain chains-1]
  (println "single section:" chain (chain-distance chain)))

(defn extend-chains [chains]
  (for [chain chains]
    (let [starting-node (first-node-of-section (first chain))
          preceding (get main-street-sections-by-last-node starting-node nil)]
      (if preceding
        (cons (second preceding) chain)
        chain))))

(defn extend-chains-fully [chains measure]
  (if (> (count measure) 0)
    (extend-chains (extend-chains-fully chains
                                        (rest measure)))
    chains))

(def chains-full
  ;; Each chain is a sequence of ways that share start/end nodes.
  ;; Each way may occur in more than one chain.
  (extend-chains-fully chains-1 chains-1))

(doseq [chain chains-full]
  (println "multiple section:" (count chain))
  (let [first-node (first-node-of-chain chain)
        last-node (last-node-of-chain chain)]
    (println "  first node:" first-node "at" (latlon-of-point first-node))
    (println "  last node:" last-node "at" (latlon-of-point last-node))
    (println "  from:" (osm-url-of-point first-node))
    (println "  to:" (osm-url-of-point last-node)))
  (doseq [section chain]
    (println "  section:" section (chain-distance chain))))

(defn same-values [a b]
  (into {}
        (for [k (into (set (keys a)) (keys b))
              :when (= (a k) (b k))]
          [k (a k)])))

(defn combine-ways [ways]
  (reduce (fn [a b]
            (dissoc (assoc (into a b)
                           "nodes" (concat (a "nodes") (rest (b "nodes")))
                           "tags" (same-values (a "tags") (b "tags")))
                    "id"))
          ways))

(def chains-merged
  (map combine-ways chains-full))

(doseq [combined chains-merged]
  (println "combined chain:" combined))
