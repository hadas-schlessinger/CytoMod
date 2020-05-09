import React, {useState, useEffect} from 'react'
import OverviewPanel from './OverviewPanel'
import ModelsClusteringPanel from './ModelsClusteringPanel'
import ModelsCorrelationPanel from './ModelsCorrelationPanel'
import OutcomAnalysis from './OutcomAnalysis'
import { Tab } from 'semantic-ui-react'
import { useHistory } from "react-router-dom";
import * as ResultsService from '../../services/ResultsService'
import beckgroungTransperant from '../../beckgroungTransperant.png'



export default function Results({state}) {
  const [oldProject, setOldProjec] = useState(false)
  const [error, setError] = useState(false)
  const [data, setdata] = useState('')
  const [gotResults, setGotResults] = useState(false)
  const [name, setName] = useState("")
  const [id, setID] = useState("")

  function onSubmit() {
    results(id)
  }


  const results = (id) => {
    if(id != null ){
      ResultsService.getResults(id).then((response) =>{
        const data = response.data
        setdata(data)
        setOldProjec(false)
        setGotResults(true)
      
      //   if (response.data.status == "DONE"){
      //     setSuccess(true)
      //     navigateTo("results")
      //  }
      }).catch((e)=>{
        console.log(e)
        setError(true)
  
      })
    }}
    
  useEffect(() => {
    console.log({state: state})
    if(state==null && name == "")
    {   
        setOldProjec(true)

    }
    else if(state.name != null && state.id != null){
      setName(state.name)
      setID(state.id)
      results(state.id)

    }
    else if(id != ""){
      results(id)
    }
    
    return () => {
     
    }
  }, [])

  const panes = [
      { menuItem: 'Overview', render: () => <Tab.Pane>{< OverviewPanel id = {id} results = {data}/ >}</Tab.Pane> },
      { menuItem: 'Models Clustering', render: () => <Tab.Pane>{< ModelsClusteringPanel id = {id} results = {data}/>}</Tab.Pane> },
      { menuItem: 'Models Correlations', render: () => <Tab.Pane>{< ModelsCorrelationPanel id = {id} results = {data}/>}</Tab.Pane> },
      { menuItem: 'Outcom Analysis', render: () => <Tab.Pane>{< OutcomAnalysis id = {id} results = {data}/>}</Tab.Pane> }]
  



return ( 
 
    <div>
      {oldProject && 
    <Tab style={{fontSize: 20}} 
      menu={{ fluid: true, vertical: true, tabular: true }} 
      grid={{paneWidth: 14, tabWidth: 2}} 
      panes={[
        {menuItem: 'Old Results', render: () => <Tab.Pane>{ <div style={{backgroundImage: `url(${beckgroungTransperant})`}} >
        <form>
        <h3>Results for old project</h3>
          <p>please insert your old project id</p>
          <p>please note - the results will only be shown if the analysis occured in the past week</p>
        <label>Id</label>
        <input type="text" name="id" placeholder="id" onChange={event => setID(event.target.value)}/ >            </form>
        <p></p>
        <input type="submit" value="Submit" onClick={(event) => onSubmit(event)}/>
        <p>Clicking the "Submit" button, will return old project results</p>
          </div>}</Tab.Pane>}]}
      />               
               
                }
      {(gotResults) && 
      <div>
      <Tab style={{fontSize: 20}} 
      menu={{ fluid: true, vertical: true, tabular: true }} 
      grid={{paneWidth: 14, tabWidth: 2}} 
      panes={panes}
      />
      {error &&  <h3 style = {{ textAlign: "center" }} className='error'>sorry can not render the page</h3>}
      </div>}
      {/* {oldProject &&  'add bot for old results'} */}
    </div>
    
    )
}






   


