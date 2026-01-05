;; experimenting with the core logic for txtosm:

(ns jcgs.street
  (:require [
             cheshire.core :refer :all ; for JSON
             ]))

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

(def points
  "A map from point IDs to their latitudes and longitudes."
  (into {}
        (for [p (filter #(= (% "type") "node")
                        raw-elements)]
          {(p "id")
           [(p "lat") (p "lon")]})))
;; (println (str (count points) " points"))

(def highway-ways
  ;; All the ways in the data that represent any kind of highway
  (into {}
        (for [p (filter #(and (= (% "type") "way")
                              (get-in % ["tags" "highway"]))
                        raw-elements)]
          {(p "id") p})))

;; (println "highway ways are:" highway-ways)

(def highway-names
  ;; A set of all the highway names in the data
  (into (set())
        (filter identity
                (for [w (vals highway-ways)]
                  (get-in w ["tags" "name"])))))

(println "highway names:" highway-names)

(def highway-way-groups-by-name
  ;; A map from highway names to maps of way-IDs to ways
  (into {}
        (for [n highway-names]
          {n (into {}
                   (for [id-hw (seq highway-ways)
                         :when (= (get-in (second id-hw) ["tags" "name"])
                                  n)]
                     id-hw))})))

(doseq [nv highway-way-groups-by-name]
  (println "group by name:" (key nv) (val nv)))

(defn latlon-of-point [point-id]
  "Look up a point-id in the points map."
  (points point-id))

(defn osm-url-of-point [point-id]
  "Return an OSM URL for a point, using the optional marker.
Handy for seeing where things are, for debugging."
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
  "Return the distance between two points.
  The input can be given as two points, which are either point
  IDs (numbers) or pairs of latitude and longitude; or it can be give
  as latitude and longitude of each point."
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
  "Return the initial bearing from one point to another.
  The input can be given as two points, which are either point
  IDs (numbers) or pairs of latitude and longitude; or it can be give
  as latitude and longitude of each point."
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
  "Return the distance along a way, following all its points.
The argument may be either a way dictionary, or a list of nodes."
  (let [nodes (if (map? way)
                (way "nodes")
                way)]
    (reduce + (map distance
                   nodes
                   (rest nodes)))))

(defn chain-distance [chain]
  "Calculate the total distance along a list of ways which are
chained together by their last->first nodes."
  (reduce +
          (map way-distance
               chain)))

(def main-street (into {} (filter #(= (get-in (second %) ["tags" "name"])
                                      street-name)
                                  highway-ways)))

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
  ;; For quickly finding a section that follows on from another
  ;; section (by having as its first node the last node of the other
  ;; section).
  (into {}
        (for [section (seq main-street)]
          {(first-node-of-section (second section)) section})))

(def main-street-sections-by-last-node
  ;; For quickly finding a section that leads onto another section (by
  ;; having as its last node the first node of the other section).
  (into {}
        (for [section (seq main-street)]
          {(last-node-of-section (second section)) section})))

(println "main street has" (count main-street-sections-by-first-node) "sections by first node:")
(doseq [keyval main-street-sections-by-first-node]
  (println (key keyval) (val keyval)))

(def chains-by-way-name
  (into {} (for [street-name highway-names]
             {street-name (list
                           (into {}
                                 (filter #(= (get-in % ["tags" "name"])
                                             street-name)
                                         (vals highway-ways))))})))

(doseq [thing (seq chains-by-way-name)]
  (println "thing" thing))

(doseq [[name parts] (seq chains-by-way-name)]
  (println "    Named highway:" name)
  ;; (doseq [[id section] (seq parts)]
  ;;   (println "         ID-ed highway section:" id section))
  )

(def chains-1
  (for [[_ section] (seq main-street)]
    (list section)))

(doseq [chain chains-1]
  (println "single section:" chain (chain-distance chain)))

(defn link-chains [chains]
  (println "link-chains" chains)
  (for [chain chains]
    (let [starting-node (first-node-of-section (first chain))
          preceding (get main-street-sections-by-last-node starting-node nil)]
      (if preceding
        (cons (second preceding) chain)
        chain))))

(defn link-chains-fully [chains measure]
  (if (> (count measure) 0)
    (link-chains (link-chains-fully chains
                                    (rest measure)))
    chains))

(def linked-chains-by-way-name
  (into {} (for [[name chainset] chains-by-way-name]
             {name
              (link-chains-fully chainset chainset)})))

;; (doseq [named (seq linked-chains-by-way-name)]
;;   (println "    Named highway:" (first named))
;;   (doseq [ided (seq (second named))]
;;     (println "         Linked ID-ed highway section:" (first ided) (second ided))))

(def chains-full
  ;; Each chain is a sequence of ways that share start/end nodes.
  ;; Each way may occur in more than one chain.
  (link-chains-fully chains-1 chains-1))

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

;; useful later: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
