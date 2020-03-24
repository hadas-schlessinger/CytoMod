// import { Tab, Tabs } from "@blueprintjs/core";
import React from 'react'
import  MethodExplanationPanel  from './MethodExplanationPanel'
import { Tab } from 'semantic-ui-react'

const panes = [
  { menuItem: 'Method Explanation', render: () => <Tab.Pane>{< MethodExplanationPanel />}</Tab.Pane> },
  { menuItem: 'Example', render: () => <Tab.Pane>Tab 2 Content</Tab.Pane> },
  { menuItem: 'Contact', render: () => <Tab.Pane>Tab 3 Content</Tab.Pane> },
]

const SideBar = () => (
  <Tab menu={{ fluid: true, vertical: true, tabular: true }} panes={panes} />
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
 
