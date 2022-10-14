import React from "react";
import {createRoot} from "react-dom/client";

import {App} from "./App.jsx";

const container = document.getElementById('root');
const root = createRoot(container);
const movies = JSON.parse(document.getElementById('movies').textContent);
let rating_counter = JSON.parse(document.getElementById('rating_counter').textContent);
root.render(<App movies={movies} rating_counter={rating_counter}/>)
