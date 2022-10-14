import {Transition} from "react-transition-group";
import {Title} from "./components/Title.jsx";
import React, {useEffect, useState} from "react";
import styled from "styled-components";

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
    const [leftMovies, changeLeftMovies] = useState(10 - rating_counter)
    const onClick = () => {
        changeShow(prev => {
            if (leftMovies === 0) {
                setTimeout(() => {
                    window.location.pathname = "/"
                }, 5000)
                return prev
            }

            if (prev) {
                currentMovieIndex += 1
                changeLeftMovies(currentCounter => {
                    return currentCounter - 1
                })
            }

            setTimeout(() => {
                changeShow(prev)
                changeTitle(<Title movie={movies[currentMovieIndex]} callback={onClick}/>)
            }, 120)
            return !prev
        });
    };


    const [title, changeTitle] = useState(<Title movie={movies[currentMovieIndex]} callback={onClick}/>);

    useEffect(() => changeShow(true))

    return (<div>

        <button onClick={onClick}></button>
        <h1 className="pt-3 text-center text-white text-3xl title-font font-medium mb-1">Faltan {leftMovies} películas
                                                                                         por calificar</h1>
        <Transition mountOnEnter unmountOnExit timeout={600} in={show}>
            {state => {
                return <Div className={state}>{title}</Div>;
            }}
        </Transition>
    </div>);
}
