import React, { useEffect } from 'react'

export default function ImageView(props) { 

    const decoder = (img) => {
        if(img != 'not'){
            var image = new Image();
        var cleanImange = img.substring(2, img.length - 1)
        image.src = `data:image/png;base64,${cleanImange}`;
        return(image.src)
        }
        else{
            return('')
        }
    }
    console.log(props.results.location[props.row])
    if(props.results.location[props.row]==props.location){
        if(props.results.type[props.row]=='image')
        return (
            <React.Fragment>
                <tr>
                <td>
                <h3>Image: {props.results.headline[props.row]}</h3>
                <p>Explanation: bbbbblalalalalalalalalaallaallalaalalalalalalalalalalalalalall</p>
                <a download = {String(props.results.headline[props.row]) + '.png'} href= {decoder(props.results.image[props.row])} title={props.results.headline[props.row]} >                    
                <img src = {decoder(props.results.image[props.row])} width = {props.results.width[props.row]} height = {props.results.height[props.row]}/></a>
                </td>
                </tr>
    
                
                </React.Fragment>

        )
    }
    return(
        <p></p>
    )
        
   }

