import React, { useState, useEffect} from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import ImageView from './ImageView';
import ModulesView from './ModulesView';

export default function OverviewPanel(props) {
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
                 <h1>Overview for project {props.projectName}</h1>
                 <h2>Modules</h2>
                 {rows.map(row =>                  
                    <ModulesView results = {props.results} row = {row} />
                    )
                }
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
