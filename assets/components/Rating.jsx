import ReactStars from "react-rating-stars-component";
import React from 'react';

export function Rating({callback}) {

    const ratingChanged = (newRating) => {
        callback()
    };

    return <ReactStars
        classNames={"flex items-center"}
        count={10}
        onChange={ratingChanged}
        size={52}
        activeColor="#ffd700"
    />
}
