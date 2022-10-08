import React from "react";
import {createRoot} from "react-dom/client";

import {App} from "./App.jsx";

const container = document.getElementById('root');
const root = createRoot(container);
const movies = JSON.parse(document.getElementById('movies').textContent);
root.render(<App movies={movies}/>)
