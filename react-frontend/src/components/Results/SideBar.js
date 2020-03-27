import React from 'react'
import OverviewPanel from './OverviewPanel'
import ModelsClusteringPanel from './ModelsClusteringPanel'
import ModelsCorrelationPanel from './ModelsCorrelationPanel'
import OutcomAnalysis from './OutcomAnalysis'
import { Tab } from 'semantic-ui-react'


const panes = [
  { menuItem: 'Overview', render: () => <Tab.Pane>{< OverviewPanel / >}</Tab.Pane> },
  { menuItem: 'Models Clustering', render: () => <Tab.Pane>{< ModelsClusteringPanel />}</Tab.Pane> },
  { menuItem: 'Models Correlations', render: () => <Tab.Pane>{< ModelsCorrelationPanel />}</Tab.Pane> },
  { menuItem: 'Outcom Analysis', render: () => <Tab.Pane>{< OutcomAnalysis />}</Tab.Pane> },
  
]

const SideBar = () => (
  <div>
    <Tab style={{fontSize: 20}} menu={{ fluid: true, vertical: true, tabular: true }} grid={{paneWidth: 14, tabWidth: 2}} panes={panes}>
    </Tab>
  </div>
  
)

export default SideBar


   


