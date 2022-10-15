import {Transition} from "react-transition-group";
import {Title} from "./components/Title.jsx";
import React, {useEffect, useState} from "react";
import styled from "styled-components";
import ClipLoader from 'react-spinners/ClipLoader';

const Div = styled.div`
  transition: 0.2s;
  /* Hidden init state */
  opacity: 0;
  transform: translateY(-10px);
  &.enter,
  &.entered {
    /* Animate in state */
    opacity: 1;
    transform: translateY(0px);
  }
  &.exit,
  &.exited {
    /* Animate out state */
    opacity: 0;
    transform: translateY(-10px);
  }
`;

export function App({movies, rating_counter}) {

    let currentMovieIndex = 0;

    const [show, changeShow] = useState(false);
    const [showError, changeShowErrror] = useState(false)
    const [showLoading, changeShowLoading] = useState(false)
    const [leftMovies, changeLeftMovies] = useState(10 - rating_counter)

    const triggerTraining = () => {
        changeShowLoading(true)
        fetch('/api/titles/train', {
            method: "GET", headers: {
                "Content-type": "application/json;charset=UTF-8", "X-CSRFToken": csrftoken
            }, mode: 'same-origin'
        })
            .then(response => response.json())
            .then(json => window.location.pathname = "/")
            .catch(err => {
                console.error(err)
                changeShowErrror(true)
            })
    }

    const onClick = () => {
        changeShow(prev => {
            changeLeftMovies(currentCounter => {
                console.log(currentCounter)
                if (currentCounter - 1 === 0) {
                    triggerTraining()
                    changeTitle(null)
                }
                return currentCounter - 1
            })
            if (leftMovies === 0) {
                return prev
            }

            if (prev) {
                currentMovieIndex += 1
            }

            setTimeout(() => {
                changeShow(prev)
                changeTitle(prevTitle => {
                    if (prevTitle === null) {
                        changeShow(true)
                        return null
                    }
                    return <Title movie={movies[currentMovieIndex]} callback={onClick}/>
                })
            }, 120)
            return !prev
        });
    };


    const [title, changeTitle] = useState(<Title movie={movies[currentMovieIndex]} callback={onClick}/>);
    const error = <h1 className="text-center text-3xl text-danger text-white">
        Ups! Algo salió mal. No eres tú, soy yo.
    </h1>
    useEffect(() => {
        changeShow(true)
    })
    return (<div>

        <button onClick={onClick}></button>

        <h1 className="pt-3 text-center text-white text-3xl title-font font-medium mb-1">
            {leftMovies ? <p> Faltan {leftMovies} películas por calificar </p> :
                <p> Has terminado, en un momento empezamos! </p>}
        </h1>

        <Transition mountOnEnter unmountOnExit timeout={600} in={show}>
            {state => {
                return <Div className={state}>
                    <div className="mt-16 flex">
                        <ClipLoader color={'#fff'} className="mx-auto" loading={showLoading} size={150}/>
                    </div>
                    {showError && error}
                    {title && title}
                </Div>;
            }}
        </Transition>
    </div>);
}
