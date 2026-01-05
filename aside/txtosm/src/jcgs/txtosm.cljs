(ns ^:figwheel-hooks jcgs.txtosm
  (:require
   [goog.dom :as gdom]
   [reagent.dom :as rdom]
   [reagent.core :as r]
   [overpass-frontend :as ovps]
   ))

(declare show-status!)
(declare get-map-data!)

(println "This text is printed from src/jcgs/txtosm.cljs. Go ahead and edit it and see reloading in action G.")

;; some queries carried over from my earlier experiments on node:

(def query-a-0
  "way[name=\"Štúrova\"];node(around:40)[amenity~\".\"]")

(def query-a-1
  "way[name=\"Štúrova\"]->.street;(node(around.street:30)[amenity~\".\"];way(around.street:30)[building~\".\"])")

;; this one is pretty close to the output I want; it may need a few more PoI types than amenity

(def query-a-2
  "[out:json][timeout:25];
  area[name=\"Bratislava\"];
  way(area)[name=\"Štúrova\"]->.my_street;
  (
        nw[amenity](around.my_street:25);
        nwr[building](around.my_street:25);
        wr[highway](around.my_street:25);
  );
  (._;>;);
  out;
")

(def bbox-a
  (clj->js {:minlat 48.14, :maxlat 48.15,
            :minlon 17.11, :maxlon 17.12 }))

(def query-b-0
  "    area[name=\"Tirana\"];
    way[name=\"Rruga Urani Pano\"]->.street;
    (
        way(around.street:30)[building~\".\"];
        node(around.street:30)[amenity~\".\"];
        node(around.street:30)[tourism~\".\"];
        node(around.street:30)[shop~\".\"];
        node(around.street:30)[office~\".\"];
        way(around.street:0)[highway~\".\"];
    );")

;; Other streets to try:
;; St John Street, London: https://www.openstreetmap.org/way/38752553
;; High Street, Porlock: https://www.openstreetmap.org/way/149883088
;; Αλεπού - Πέλεκας, Pelekas, Corfu: https://www.openstreetmap.org/way/618264889

(def bbox-b
  (clj->js {:minlat 41.30, :maxlat 41.32,
            :minlon 18.80, :maxlon 19.83 }))

;; define your app data so that it doesn't get over-written on reload
(let [overpass (new ovps "//overpass-api.de/api/interpreter")]
  (defonce app-state (atom
                      {:text "Hello textually mapped world!"
                       :title "street name to go here followed by things"
                       :status "not yet activated"
                       :overpass overpass
                       :api-results ["thing one" "thing two"]
                       :rows []})))

(defn title []
  [:h1 (:title @app-state)])

(defn debug-item [item]
  [:li {:class "debugitem"
        :key (str item)}
   (str "item " item " for debug")])

(def latest-result nil)
(def latest-error nil)

(defn fetch! []
  (println "Fetching from Overpass A")
  ;; (show-status! "Fetching from Overpass")
  (get-map-data!)
  (println "Fetch initiated"))

(def query-options
  (clj->js { :properties (js->clj (. ovps -ALL)) }))

(defn app []
  [:div {:class "app"}
   [title]
   [:div {:class "textualmap"}
    [:button {:on-click fetch!} "Go"]
    [:p (:status @app-state)]
    ;; [:ul
    ;;  (for [item (:api-results @app-state)]
    ;;    [(debug-item item)])]
    [:div
     [:dl
      [:dt "Query options"] [:dd (str (js->clj query-options))]
      [:dt "Overpass object"][:dd (str (:overpass @app-state))]]]
    ]])

(defn mount-app-element []
  (rdom/render [app] (gdom/getElement "app")))

(defn show-status! [status]
  (swap! @app-state update-in [:status] status)
  (mount-app-element))

(defn ^:export handle-result [err raw-result]
  (let [result (js->clj raw-result)]
    (println (str "handle-result result is " result " and err is " err))
    (set! latest-result result)
    (set! latest-error err)
    (show-status! "Fetched from Overpass")
    (if result
      (swap! @app-state update-in [:api-results] (constantly result))
      (println (str "error: " err)))))

(defn ^:export handle-error [err]
  (when err
    (show-status! "Error in fetching from Overpass")
    (println (str "handle-error err is" err))))

(def query-sending-result nil)

(defn get-map-data! []
  ;; Set the query in motion.
  ;;
  ;; No useful return value from this --- the result comes back
  ;; through callbacks.
  (println "In get-map-data! about to call JS")
  ;; the following print output looks correct, it shows a plausible function:
  (println (str "query function is " (. (:overpass @app-state) -BBoxQuery)))
  (println (str "query is " query-a-2))
  (println (str "bbox is " bbox-a " which is " (js->clj bbox-a)))
  (println (str "options are " query-options " which is " (js->clj query-options)))
  (println (str "result callback is " (fn [e r] (jcgs.txtosm/handle-result e r))))
  (println (str "error callback is "(fn [e] (jcgs.txtosm/handle-error e))))
  ;; however something goes wrong around here, as it never prints the following print output
  ;;
  ;; I think I may have hit something described in
  ;; https://www.verypossible.com/insights/clojurescript-and-javascript-interoperability-a-comprehensive-guide#pitfalls
  ;; where it gives:
  ;; call(. (. js/document -getElementsByTagName) call js/document "html")
  ;; bind((. (. js/document -getElementsByTagName) bind js/document) "html")
  ;; and says it looks odd and should probably be avoided
  (set! query-sending-result
        ;; this is meant to be equivalent to https://github.com/plepe/overpass-frontend/blob/master/example-bbox.js
        ;; my original
        ;; (. (:overpass @app-state) BBoxQuery
        ;;    query-a-2 bbox-a
        ;;    query-options
        ;;    ;; I wrapped these as I suspected that calling them
        ;;    ;; directly wasn't working; but I'm not sure that they're
        ;;    ;; working like this too; and now they're wrapped, I guess
        ;;    ;; I don't really need to give the namespace:
        ;;    (fn [e r] (jcgs.txtosm/handle-result e r))
        ;;    (fn [e] (jcgs.txtosm/handle-error e)))

        ;; based on verypossible:
        (.call (. (:overpass @app-state) -BBoxQuery)
               query-a-2 bbox-a
               query-options
               ;; I wrapped these as I suspected that calling them
               ;; directly wasn't working; but I'm not sure that they're
               ;; working like this too; and now they're wrapped, I guess
               ;; I don't really need to give the namespace:
               (fn [e r] (jcgs.txtosm/handle-result e r))
               (fn [e] (jcgs.txtosm/handle-error e)))
        )
  (println (str "query-sending-result: " query-sending-result)))

(mount-app-element)

;; ;; specify reload hook with ^:after-load metadata
(defn ^:after-load on-reload []
  ;; optionally touch your app-state to force rerendering depending on
  ;; your application
  ;; (swap! app-state update-in [:__figwheel_counter] inc)
  (fetch!)
  (mount-app-element)                   ; TODO: should this be here?
  )
