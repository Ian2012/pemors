import React, {useEffect, useState} from 'react';

export function RecommenderTitle({title}) {
    const [poster, setPoster] = useState('')
    const fetchData = () => {
        fetch(`https://www.omdbapi.com/?i=${title.id}&apikey=6aad63ad`)
            .then(response => {
                return response.json()
            })
            .then(data => {
                console.log("OMDB: ", data)
                setPoster(data['Poster'] === "N/A" ? "https://cdn-icons-png.flaticon.com/512/103/103085.png" : data['Poster'])
                title.omdb = data
                title.rating = data["imdbRating"] === "N/A" ? 0 : data["imdbRating"]
                title.votes = data["imdbVotes"] === "N/A" ? 0 : data["imdbVotes"]
                title.votes = data["imdbVotes"] === "N/A" ? 0 : data["imdbVotes"]
            })
    }
    useEffect(() => fetchData())

    return <div key={title.id} className="mt-8">
        <a href={"/title" + title.id}>
            <img id="{{ values.title.id }}"
                 src={poster && poster}
                 alt="poster"
                 className="hover:opacity-75 transition ease-in-out duration-150"></img>
        </a>
        <div className="mt-2">
            <a href="assets/components/Recommender/RecommenderTitle"
               className="text-lg mt-2 hover:text-gray-300">{title.primary_title}</a>
            <div className="flex items-center text-gray-400 text-sm mt-1">
                <svg className="fill-current text-orange-500 w-4" viewBox="0 0 24 24">
                    <g data-name="Layer 2">
                        <path
                            d="M17.56 21a1 1 0 01-.46-.11L12 18.22l-5.1 2.67a1 1 0 01-1.45-1.06l1-5.63-4.12-4a1 1 0 01-.25-1 1 1 0 01.81-.68l5.7-.83 2.51-5.13a1 1 0 011.8 0l2.54 5.12 5.7.83a1 1 0 01.81.68 1 1 0 01-.25 1l-4.12 4 1 5.63a1 1 0 01-.4 1 1 1 0 01-.62.18z"
                            data-name="star"></path>
                    </g>
                </svg>
                <p className="block">Rating: {title.rating}</p>
            </div>

        </div>
    </div>
}

/*
{title.omdb &&
                <div className="text-gray-400 text-sm">{title.ombd.Plot}</div>
            }
 */
