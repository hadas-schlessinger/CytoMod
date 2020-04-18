import React,  {useState, useEffect} from 'react'
import LoadingPage from './LoadingPage';
import { useHistory } from "react-router-dom";
import * as SetParams from  '../../services/SetParams'



export default function Calculating(props) {
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(false);
  const history = useHistory();

    const request = () => {
      if(props.projectName==null || props.formID==null)
      {
        navigateTo("set")
      }
      console.log(props.projectName, props.formID)
      SetParams.methodStatus(props.projectName, props.formID.id).then((response) =>{
        console.log({data: response.data.status});
        if (response.data.status == "DONE"){
          setSuccess(true)
          navigateTo("results")
       }
      }).catch((e)=>{
        console.log(e)
      })
  }
      
        const interval = setInterval(() => {
        request()
        }, 1000*60)  
       

     function navigateTo(serviceName) {
    history.push(`/${serviceName}`);
  }
    
      return (
        <div style={{height: '100%', width:'100%'}}>
            <h2 style={{color: '#194d33', fontSize: 18, textAlign: 'center'}}>Your project ID is - {props.formID.id}</h2>
            <h2 style={{color: '#194d33', fontSize: 18, textAlign: 'center'}}>Your project name is -{props.projectName} </h2>
            <LoadingPage/>
            {interval}
            {success && clearInterval(interval)}
            {success &&  navigateTo("results")}
               
        </div>
    )
}
