import React, {useState, useEffect} from 'react'
import OverviewPanel from './OverviewPanel'
import ModelsClusteringPanel from './ModelsClusteringPanel'
import ModelsCorrelationPanel from './ModelsCorrelationPanel'
import OutcomAnalysis from './OutcomAnalysis'
import { Tab } from 'semantic-ui-react'
import { useHistory } from "react-router-dom";
import * as ResultsService from '../../services/ResultsService'
import beckgroungTransperant from '../../beckgroungTransperant.png'



export default function Results(props) {
  const [oldProject, setOldProjec] = useState(false)
  const [error, setError] = useState(false)
  const [data, setdata] = useState('')
  const [gotResults, setGotResults] = useState(false)
  const [name, setName] = useState("")
  const [id, setID] = useState("")

  function onSubmit() {
    console.log(name)
    results()
  }


  const results = () => {
      ResultsService.getResults(props.projectName).then((response) =>{
        const data = response.data
        setdata(data)
        console.log({data: data});
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
    }
    
  useEffect(() => {
    console.log(props.projectName)
    if(props.projectName != null ){
      setName(props.projectName)
      results()

    }
    if(props.projectName==null && name == "")
    {   
        setOldProjec(true)

    }
    if(name != ""){
      results()
    }
    
    return () => {
     
    }
  }, [])

  const panes = [
      { menuItem: 'Overview', render: () => <Tab.Pane>{< OverviewPanel projectName = {name} results = {data}/ >}</Tab.Pane> },
      { menuItem: 'Models Clustering', render: () => <Tab.Pane>{< ModelsClusteringPanel />}</Tab.Pane> },
      { menuItem: 'Models Correlations', render: () => <Tab.Pane>{< ModelsCorrelationPanel />}</Tab.Pane> },
      { menuItem: 'Outcom Analysis', render: () => <Tab.Pane>{< OutcomAnalysis />}</Tab.Pane> }]
  



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
          <p>please insert your old project name and id</p>
          <p>please note - the results will only be shown if the analysis occured in the past week</p>
        <label>Name</label>
        <input type="text" name="name_data" placeholder="project name" onChange={event => setName(event.target.value)}/ >
  
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






   


