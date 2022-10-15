import React, {useEffect, useState} from 'react';
import {Rating} from "./Rating.jsx";
import ClipLoader from "react-spinners/ClipLoader";

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

    return <section className="text-gray-100 body-font overflow-hidden">
        <div className="container px-5 py-6 mx-auto">
            <div className="lg:w-4/5 mx-auto flex flex-wrap justify-center">
                {poster ? <img alt="ecommerce"
                               className="min-h-[32rem] lg:w-1/2 max-h-[550px] lg:h-auto h-64 object-contain object-center rounded"
                               src={poster}></img>
                    :
                    <div
                        className="mt-16 flex min-h-[32rem] lg:w-1/2 max-h-[550px] lg:h-auto h-64 object-contain object-center rounded">
                        <ClipLoader color={'#fff'} className="mx-auto my-auto" size={150}/>
                    </div>
                }
                <div className="lg:w-1/2 w-full lg:pl-10 lg:py-6 mt-6 lg:mt-0">
                    <h1 className="text-3xl title-font font-medium mb-1">{movie.primary_title}</h1>
                    <div className="flex mb-4">
                        <span className="flex">
                            {movie.omdb && <span
                                className="text-gray-400">{movie.omdb.imdbVotes === "N/A" ? 0 : movie.omdb.imdbVotes} Reviews</span>}
                        </span>
                    </div>
                    {movie.omdb && <p className="leading-relaxed md:text-blue">
                        {movie.omdb.Plot}
                    </p>}
                    <div className="mx-auto">
                        <Rating key={new Date().getTime()} movie={movie} callback={callback}></Rating>
                    </div>
                </div>
            </div>
        </div>
    </section>
}
