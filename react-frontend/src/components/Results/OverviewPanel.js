import React, { useState, useEffect } from 'react'
import beckgroungTransperant from '../../beckgroungTransperant.png'
import { useHistory } from "react-router-dom";

export default function OverviewPanel(props) {
    const [hasResults, sethasResults] = useState(false)
    const [results, setResults] = useState({})

   
    
    // function onSubmit() {
    //     setOldProject(false)
    //     console.log(name)
    //    navigateTo('results')       
    //   }
    
//       function navigateTo(serviceName) {
//         history.push(`/${serviceName}`, name);
//    }
    useEffect(() => {
        console.log({results: results})
        console.log({results_prop: props.results})
        if(props.results!=''){
            setResults(props.results)
            sethasResults(true)
        }
        // if(results!=''){
        //     console.log({results_after_change: results})
        //     sethasResults(true)

        //     // var image = new Image();
        //     // image.src = 'data:image/png;base64,'+props.results.image.row_1

        // }
        return () => {  
            // <div>  
            // <tr>
            // <td style="color: #0B7478"><span style= "font-size: 16pt;">yayy </span></td>
            // <img src={'data:image/png;base64,'+props.results.image.row_1} >      </img>
            // </tr>    
            // </div>       
        }
    }, [])

    const decoder = (img) => {
        var image = img
        console.log({image: img})

        var src = `data:image/png;base64,${props.results.image.row_1}`
        console.log({src: src})
        

    }

  
    console.log(props.results.image.row_1)
    return (
        <div style={{backgroundImage: `url(${beckgroungTransperant})`}}>           
            
                 <h1>Overview for project {props.projectName}</h1>
                 <h2>image:</h2>
                 {/* <tr>
                <td style="color: #0B7478"><span style= "font-size: 16pt;">yayy </span></td> */}
                { hasResults && 
                    <img src = {`data:image/png;base64,${props.results.image.row_2}`} width ={400} lengh = {400}/>  
                }
                
                {/* </tr>   */}
               
            

         
           
            
        </div>
    )
}
