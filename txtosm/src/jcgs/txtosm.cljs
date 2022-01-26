(ns ^:figwheel-hooks jcgs.txtosm
  (:require
   [goog.dom :as gdom]
   [reagent.dom :as rdom]
   [reagent.core :as r]
   [overpass-frontend :as ovps]
   ))

(println "This text is printed from src/jcgs/txtosm.cljs. Go ahead and edit it and see reloading in action G.")

;; (js/console.log "ovps")

;; define your app data so that it doesn't get over-written on reload
(defonce app-state (atom
                    {:text "Hello textually mapped world!"
                     :title "street name to go here followed by things"
                     :api-results ["thing one" "thing two"]
                     :overpass (new ovps "//overpass-api.de/api/interpreter")
                     :rows []}))

(defn title []
  [:h1 (:title @app-state)])

(defn get-app-element []
  (gdom/getElement "app"))

(defn debug-item [item]
  [:li {:class "debugitem"
        :key (str item)}
   (str "item " item " for debug")])

(defn app []
  [:div {:class "app"}
   [title]
   [:div {:class "textualmap"}
    [:ul
    (for [item (:api-results @app-state)]
      [debug-item item])]
    [:div
     [:pre
      (str (:overpass @app-state))]]]])

(defn mount-app-element []
  (rdom/render [app] (get-app-element)))

(mount-app-element)

;; ;; specify reload hook with ^:after-load metadata
(defn ^:after-load on-reload []
  ;; optionally touch your app-state to force rerendering depending on
  ;; your application
  ;; (swap! app-state update-in [:__figwheel_counter] inc)
  (mount-app-element)                   ; TODO: should this be here?
  )

