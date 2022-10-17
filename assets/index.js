import React, {lazy, Suspense} from "react";
import {createRoot} from "react-dom/client";


const Coldstart = lazy(() => import ("./components/Coldstart/Coldstart.jsx"))
const Recommender = lazy(() => import ("./components/Recommender/Recommender.jsx"))

const elements = [
    document.getElementById("coldstart"),
    document.getElementById("movie_recommendation"),
]

const apps = [
    <Suspense fallback={<div>Loading...</div>}>
        <Coldstart/>
    </Suspense>,
    <Suspense fallback={<div>Loading...</div>}>
        <Recommender/>
    </Suspense>,
]

for (let i in elements) {
    let element = elements[i]
    let app = apps[i]

    if (element !== null) {
        createRoot(element).render(app)
    }
}
