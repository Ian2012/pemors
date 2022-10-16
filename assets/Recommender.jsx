import React from "react";


export default function Coldstart() {
    const movies = JSON.parse(document.getElementById('movies').textContent);

    return <div>
        {movies.map((movie) => <div>{movie.id}</div>)}
    </div>;
}
