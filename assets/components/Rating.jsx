import ReactStars from "react-rating-stars-component";
import React from 'react';

const ratingChanged = (newRating) => {
    console.log(newRating);
};


export function Rating() {
    return <ReactStars
        classNames={"flex items-center"}
        count={10}
        onChange={ratingChanged}
        size={24}
        activeColor="#ffd700"
    />
}
