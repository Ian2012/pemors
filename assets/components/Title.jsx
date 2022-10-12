import React, {useEffect, useState} from 'react';
import {Rating} from "./Rating.jsx";

export function Title({movie, callback}) {

    const [poster, setPoster] = useState('')
    const fetchData = () => {
        fetch(`https://www.omdbapi.com/?i=${movie.id}&apikey=6aad63ad`)
            .then(response => {
                return response.json()
            })
            .then(data => {
                console.log("OMDB: ", data)
                setPoster(data['Poster'] === "N/A" ? "https://cdn-icons-png.flaticon.com/512/103/103085.png" : data['Poster'])
                movie.omdb = data
                movie.rating = data["imdbRating"] === "N/A" ? 0 : data["imdbRating"]
                movie.votes = data["imdbVotes"] === "N/A" ? 0 : data["imdbVotes"]
                movie.votes = data["imdbVotes"] === "N/A" ? 0 : data["imdbVotes"]
            })
    }
    useEffect(() => fetchData())

    return <section className="text-gray-600 body-font overflow-hidden">
        <div className="container px-5 py-24 mx-auto">
            <div className="lg:w-4/5 mx-auto flex flex-wrap">
                {poster && <img alt="ecommerce"
                                className="lg:w-1/2 max-h-[550px] lg:h-auto h-64 object-contain object-center rounded"
                                src={poster}></img>}
                <div className="lg:w-1/2 w-full lg:pl-10 lg:py-6 mt-6 lg:mt-0">
                    <h1 className="text-gray-900 text-3xl title-font font-medium mb-1">{movie.primary_title}</h1>
                    <div className="flex mb-4">
                        <span className="flex items-center">
                            {movie.omdb && <span
                                className="text-gray-600 ml-3">{movie.omdb.imdbVotes === "N/A" ? 0 : movie.omdb.imdbVotes} Reviews</span>}
                        </span>
                        <span className="flex ml-3 pl-3 py-2 border-l-2 border-gray-200 space-x-2s">
                            Useful links
                        </span>
                    </div>
                    {movie.omdb && <p className="leading-relaxed">
                        {movie.omdb.Plot}
                    </p>}
                    <Rating movie={movie} callback={callback}></Rating>
                </div>
            </div>
        </div>
    </section>
}
