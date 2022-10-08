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

export function App({movies}) {

    let currentMovieIndex = 0;
    let moviesLength = movies.length;

    const [show, changeShow] = useState(true);

    const onClick = () => {
        changeShow(prev => {
            if (currentMovieIndex >= moviesLength - 1) {
                return prev
            }

            if (prev) {
                currentMovieIndex += 1
            }

            setTimeout(() => {
                changeShow(prev)
                changeTitle(<Title movie={movies[currentMovieIndex]} callback={onClick} poster={poster}/>)
            }, 120)
            return !prev
        });
    };

    const [title, changeTitle] = useState(<Title movie={movies[currentMovieIndex]} callback={onClick}/>);

    const [poster, setPoster] = useState('')

    const fetchData = () => {
        console.log("Fetch data")
        fetch(`http://www.omdbapi.com/?i=${movies[currentMovieIndex].id}&apikey=6aad63ad`)
            .then(response => {
                return response.json()
            })
            .then(data => {
                console.log(data)
                setPoster(data['Poster'] === "N/A" ? "https://cdn-icons-png.flaticon.com/512/103/103085.png" : data['Poster'])
            })
    }

    useEffect(() => {
        fetchData()
    }, [])

    return (
        <div>

            <button onClick={onClick}></button>
            <Transition mountOnEnter unmountOnExit timeout={200} in={show}>
                {state => {
                    return <Div className={state}>{title}</Div>;
                }}
            </Transition>
        </div>
    );
}
