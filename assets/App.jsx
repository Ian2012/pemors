import {Transition} from "react-transition-group";
import {Title} from "./components/Title.jsx";
import React, {useState} from "react";
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
const movies = JSON.parse(document.getElementById('movies').textContent);
let id = 0

export function App() {
    const [show, changeShow] = useState(true);
    const onClick = () => {
        changeShow(prev => {
            return !prev;
        });
    };
    return (
        <div>
            <button onClick={onClick}></button>
            <Transition mountOnEnter unmountOnExit timeout={200} in={show}>
                {state => {
                    return <Div className={state}><Title/></Div>;
                }}
            </Transition>
        </div>
    );
}
