import ReactStars from "react-rating-stars-component";
import React from 'react';

export default function Rating({movie, callback}) {

    const ratingChanged = (rating) => {
        fetch('/api/titles/user_rating/', {
            method: "POST",
            body: JSON.stringify({'title': movie.id, 'rating': rating}),
            headers: {
                "Content-type": "application/json;charset=UTF-8",
                "X-CSRFToken": csrftoken
            },
            mode: 'same-origin'
        })
            .then(response => response.json())
            .then(json => {
                console.log(json)
                if (callback !== undefined){
                    callback()
                }
            })
    };

    return <div className="flex justify-center">
        <ReactStars
            classNames={"flex"}
            count={10}
            onChange={ratingChanged}
            size={52}
            activeColor="#ffd700"
        />
    </div>
}
