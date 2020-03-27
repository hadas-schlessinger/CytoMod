import React from 'react'
import  UploadPanel  from './UploadPanel'
import ParametersPanel from './ParametersPanel'
import { Tab }  from 'semantic-ui-react'


const panes = [
    { menuItem: 'Upload Data', render: () => <Tab.Pane>{< UploadPanel />}</Tab.Pane> },
    { menuItem: 'Set Parameters', render: () => <Tab.Pane>{< ParametersPanel />}</Tab.Pane> },
]

const SideBar = () => (
  <Tab style={{fontSize: 20}} menu={{ fluid: true, vertical: true, tabular: true }} grid={{paneWidth: 14, tabWidth: 2}} panes={panes} />
)

export default SideBar
      
      
         




