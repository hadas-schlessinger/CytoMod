import React, { useState, useEffect} from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import ImageView from './ImageView';
import AbsModulesView from './AbsModulesView';
import AdjModulesView from './AdjModulesView';


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
                 <h1>Overview for project {props.id}</h1>
                 <h2>Modules</h2>
                 {rows.map(row =>                  
                    <AbsModulesView results = {props.results} row = {row} />
                    )
                }
                {rows.map(row =>    
                    <AdjModulesView results = {props.results} row = {row} />
                    )
                }
                <h2>Figures</h2>
                 
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
