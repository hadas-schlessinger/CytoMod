// import { Tab, Tabs } from "@blueprintjs/core";
import React from 'react'
import  MethodExplanationPanel  from './MethodExplanationPanel'
import WelcomePanel from './WelcomePanel'
import ContactPanel from './ContactPanel'
import { Tab } from 'semantic-ui-react'


const panes = [
  { menuItem: 'Welcome', render: () => <Tab.Pane>{< WelcomePanel />}</Tab.Pane> },
  { menuItem: 'Method Explanation', render: () => <Tab.Pane>{< MethodExplanationPanel />}</Tab.Pane> },
  { menuItem: 'Example', render: () => <Tab.Pane>Will Put here the Jupiter Notebook</Tab.Pane> },
  { menuItem: 'Contact', render: () => <Tab.Pane>{<ContactPanel / >}</Tab.Pane> },
]

const SideBar = () => (
  <Tab style={{fontSize: 20}} menu={{ fluid: true, vertical: true, tabular: true }} grid={{paneWidth: 14, tabWidth: 2}} panes={panes} />
)

export default SideBar


// export default function SideBar() {
//     // handleTabChange = (activeTabId) => this.setState({ activeTabId });
   

//     return (
        
//     <Tabs id="HomeTabs" onChange={this.handleTabChange} selectedTabId="ng">
//         <Tab id="ng" title="Method Explanation" panel={< MethodExplanationPanel />} />
//         <Tab id="mb" title="Example" panel={<MethodExplanationPanel />} panelClassName="ember-panel" />
//         <Tab id="rx" title="Contact" panel={<MethodExplanationPanel />} />
//     {/* <Tab id="bb" disabled title="Backbone" panel={<BackbonePanel />} /> */}
//     <Tabs.Expander />
//     {/* <input className="bp3-input" type="text" placeholder="Search..." /> */}
//     </Tabs>  
      
//     )
    
// }
 
