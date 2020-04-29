import React, { useState, useEffect} from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import ImageView from './ImageView';

export default function OverviewPanel(props) {
    const [hasResults, sethasResults] = useState(false)
    const [results, setResults] = useState({})
    const [rows, setrows] = useState([])
 
    useEffect(() => {
        console.log({results: results})
        console.log({results_prop: props.results})
        if(props.results!=''){
            setResults(props.results)
            sethasResults(true)
            setrows(Object.keys(props.results.image))
            console.log(props.results.type)
                      
        }
        return () => {     
        }
    }, [])

 
    
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>           
                 <h1>Overview for project {props.projectName}</h1>
                <h2>Figures</h2>
                 {/* <tr>
                <td style="color: #0B7478"><span style= "font-size: 16pt;">yayy </span></td> */}
                { hasResults && 
                  <table>
                  <tbody>
                {rows.map(row =>                  
                    
                    <ImageView results = {props.results} row = {row} location = 'overview'/>

                    )
                }
                </tbody>
                </table>
                }
        </div>
    )
}
