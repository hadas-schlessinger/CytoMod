import React, {useEffect, useState} from 'react'
import  UploadPanel  from './UploadPanel'
import ParametersPanel from './ParametersPanel'
import { Tab }  from 'semantic-ui-react'
import { useHistory } from 'react-router-dom'


export default function SideBar(props) {
  const history = useHistory()
  const routes = { 0: 'set',
                   1: 'set/parameters'}


 

  function handleOnTabChange(e, { activeIndex }) {
    navigateTo(routes[activeIndex]);
  }

  function navigateTo(route) {
    history.push(`/${route}`);
  }

  const panes = [
    { menuItem: 'Upload Data', render: () => <Tab.Pane>{< UploadPanel />}</Tab.Pane> },
    { menuItem: 'Set Parameters', render: () => <Tab.Pane>{< ParametersPanel />}</Tab.Pane> },
]
  
  return (<Tab style={{fontSize: 20}} 
    menu={{ fluid: true, vertical: true, tabular: true }} 
    grid={{paneWidth: 14, tabWidth: 2}} 
    panes={panes} 
    activeIndex = {props.index}
    onTabChange= {handleOnTabChange}
    />)
}
  

      
      
         




