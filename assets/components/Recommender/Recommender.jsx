import React, {useEffect, useState} from "react";
import {Transition} from "react-transition-group";
import ClipLoader from "react-spinners/ClipLoader";
import {RecommenderTitle} from "./RecommenderTitle.jsx";
import InfiniteScroll from 'react-infinite-scroll-component';

export default function Coldstart() {
    const [titles, setTitles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(0)


    const fetchTitles = () => {
        fetch(`/api/titles/recommend?page=${page}`, {
            method: "GET", headers: {
                "Content-type": "application/json;charset=UTF-8", "X-CSRFToken": csrftoken
            }, mode: 'same-origin'
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`This is an HTTP error: The status is ${response.status}`)
                }
                return response.json()
            })
            .then((json) => {
                setTitles((prevState) => {
                    setPage(current => {
                        return current + 1
                    })
                    return prevState.concat(json.movies)
                })
                setError(null)
            })
            .catch((err) => {
                setTitles(null)
                setError(err.message)
            })
            .finally(() => {
                setLoading(false)
            });
    }

    useEffect(() => {
        fetchTitles()
    }, []);

    return <div>
        <Transition mountOnEnter unmountOnExit timeout={600} in={true}>
            {state => {
                return <div className={state}>
                    {loading ? <div className="mt-16 flex">
                        <ClipLoader color={'#fff'} className="mx-auto" loading={loading} size={150}/>
                    </div> : <div className="container mx-auto px-4 pt-16">
                        <div className="popular-movies" id="custom-container">
                            <h2 className="uppercase tracking-wider text-orange-500 text-lg font-semibold">Películas
                                                                                                           recomendadas</h2>
                            <div className="">
                                <InfiniteScroll
                                    scrollThreshold={1.0}
                                    className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8"
                                    dataLength={titles.length} //This is important field to render the next data
                                    next={fetchTitles}
                                    hasMore={true}
                                    loader={loading}
                                    endMessage={<p style={{textAlign: 'center'}}>
                                        <b>Yay! You have seen it all</b>
                                    </p>}
                                >
                                    {titles && titles.map((title) => <RecommenderTitle key={title.title}
                                                                                       title={title}></RecommenderTitle>)}
                                </InfiniteScroll>
                            </div>
                        </div>
                    </div>}
                    {error && <div>Tenemos un problema, por favor intenta de nuevo</div>}

                </div>;
            }}
        </Transition>
    </div>
}
