import React, { useState, useEffect} from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import ImageView from './ImageView';



export default function ResultsSchema(props) {
    const [hasResults, sethasResults] = useState(false)
    const [rows, setrows] = useState([])
 
    useEffect(() => {
        if(props.results!=''){
            sethasResults(true)
            setrows(Object.keys(props.results.image))
                      
        }
        return () => {     
        }
    }, [])

 
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>           
                 <h1>{props.panel} Results for {props.state} Cytokines for Project {props.projectName}</h1>
                <h2>Figures</h2>
                 
                { hasResults && 
                  <table>
                  <tbody>
                {rows.map(row =>                  
                    
                    <ImageView results = {props.results} row = {row} location = {props.location}/>

                    )
                }
                </tbody>
                </table>
                }
        </div>
    )
}
