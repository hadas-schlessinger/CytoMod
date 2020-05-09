import React, { useState, useEffect} from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import ImageView from './ImageView';
import NoResults from './NoResults';



export default function ResultsSchema(props) {
    const [hasResults, sethasResults] = useState(false)
    const [NoFigures, setNoFigures] = useState(false)
    const [rows, setrows] = useState(Object.keys(props.results.image))
    
    const hasFigure = () =>{
        if(props.results!=''){
            let counter = 0
            for(const row of rows) {
                if(props.results.location[row]==props.location){
                    console.log('inn')
                    counter=counter+1
                }
            }
            console.log(counter)
            if (counter==0){
                setNoFigures(true)
            }                      
        }
       
    }

    useEffect(() => {
        if(props.results!=''){
            setrows(Object.keys(props.results.image)) 
            sethasResults(true)
        }
        hasFigure()
        // if(props.results!='' && hasFigure()){
        //     sethasResults(true)
                      
        // }
        // if(!hasFigure()){
        //     sethasResults(false) 

        // }
        return () => {     
        }
    }, [])

 
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>           
                 <h1>{props.panel} Results for {props.state} Cytokines for Project {props.id}</h1>
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
                 { NoFigures &&  <NoResults />
                
                }
        </div>
    )
}
