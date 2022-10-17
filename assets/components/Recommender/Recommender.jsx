import React, {useEffect, useState} from "react";
import {Transition} from "react-transition-group";
import ClipLoader from "react-spinners/ClipLoader";
import {RecommenderTitle} from "./RecommenderTitle.jsx";


export default function Coldstart() {
    const [titles, setTitles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch(`/api/titles/recommend`, {
            method: "GET", headers: {
                "Content-type": "application/json;charset=UTF-8", "X-CSRFToken": csrftoken
            }, mode: 'same-origin'
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(
                        `This is an HTTP error: The status is ${response.status}`
                    )
                }
                return response.json()
            })
            .then((json) => {
                setTitles(json.movies)
                setError(null)
            })
            .catch((err) => {
                setTitles(null)
                setError(err.message)
            })
            .finally(() => {
                setLoading(false)
            });
    }, []);

    return <div>
        <Transition mountOnEnter unmountOnExit timeout={600} in={true}>
            {state => {
                return <div className={state}>
                    {loading ?
                        <div className="mt-16 flex">
                            <ClipLoader color={'#fff'} className="mx-auto" loading={loading} size={150}/>
                        </div>
                        :
                        <div className="container mx-auto px-4 pt-16">
                            <div className="popular-movies">
                                <h2 className="uppercase tracking-wider text-orange-500 text-lg font-semibold">Películas
                                                                                                               recomendadas</h2>
                                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8">
                                    {titles && titles.map((title) =>
                                        <RecommenderTitle key={title.id} title={title}></RecommenderTitle>
                                    )}
                                </div>
                            </div>
                        </div>
                    }
                    {error && <div>Tenemos un problema, por favor intenta de nuevo</div>}

                </div>;
            }}
        </Transition>
    </div>
}
