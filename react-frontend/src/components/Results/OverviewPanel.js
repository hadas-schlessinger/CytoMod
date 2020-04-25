import React, { useState, useEffect } from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import { useHistory } from "react-router-dom";

export default function OverviewPanel(props) {
    const [oldProject, setOldProject] = useState(false)
    const [name, setName] = useState("")
    const [id, setID] = useState("")
    const history = useHistory();

    
    // console.log(props.results.location.row_1)
    
    function onSubmit() {
        setOldProject(false)
        console.log(name)
       navigateTo('results')       
      }
    
      function navigateTo(serviceName) {
        history.push(`/${serviceName}`, name);
   }
    // useEffect(() => {
        
    //     return () => {
    //         if(props.projectName==null){
    //             setOldProject(true)
    //         }
           
    //     }
    // }, [])

   
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>
            {/* {oldProject &&                
                <div>
                    <form>
                    <h3>Results for old project</h3>
                <p>please insert your old project name and id</p>
                <p>please note - the results will only be shown if the analysis occured in the past week</p>
            <label>Name</label>
             <input type="text" name="name_data" placeholder="project name" onChange={event => setName(event.target.value)}/ >

             <label>Id</label>
             <input type="text" name="id" placeholder="id" onChange={event => setID(event.target.value)}/ >            </form>
             <p></p>
             <input type="submit" value="Submit" onClick={(event) => onSubmit(event)}/>
             <p>Clicking the "Submit" button, will return old project results</p>
                </div>
                } */}
            {!oldProject &&
            <div>
                 <h1>Overview for project {props.projectName}</h1>
            </div>

            }
           
            
        </div>
    )
}
